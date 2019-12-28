from socket import socket, AF_INET, SOCK_DGRAM
from threading import Timer, Thread, Lock
from queue import Queue
from typing import Callable, Optional
from functools import wraps
from functools import reduce
from sys import argv

UDP = lambda: socket(AF_INET, SOCK_DGRAM)

PORT = 23150
EXPERIMENT = 1

WINDOW_SIZE = 128
MAX_PACK_SIZE = 1000
HEADER_SIZE = 9
TIMEOUT = .3
PAYLOAD_SIZE = MAX_PACK_SIZE - HEADER_SIZE

ACKNOWLEDGED_MESSAGE = b"ACKNOWLEDGED"


WHOAMI = "destination"


class Topology(type):

    router3_destination = "10.10.7.2"
    router2_destination = "10.10.5.1"
    router1_destination = "10.10.4.1"
    destination_router3 = "10.10.7.1"
    destination_router2 = "10.10.5.2"
    destination_router1 = "10.10.4.2"
    router3_source = "10.10.3.2"
    router2_source = "10.10.2.1"
    router1_source = "10.10.1.2"
    source_router3 = "10.10.3.1"
    source_router2 = "10.10.2.2"
    source_router1 = "10.10.1.1"

    __actions = ["listen", "send"]

    def __getattribute__(self, link):
        try:
            action, peer = link.split("_")
            assert action in Topology.__actions
        except ValueError:
            raise ValueError(f"format must be: [action]_[peer]. Found {link}")
        except AssertionError:
            raise TypeError(f'Action must be one of {", ".join(Topology.__actions)}')
        order = 0 if action == "listen" else 1
        names = [None, None]
        names[order] = WHOAMI
        names[(order + 1) % 2] = peer
        attr = "_".join(names)
        try:
            address = getattr(Topology, attr)

            return address
        except AttributeError:
            raise AttributeError(f"Wrong Node!. There is no link to Node {peer}")


class Interfaces(metaclass=Topology):
    pass


class Header:
    """
        Represents header of a packet.
    """

    def __init__(self, checksum: str, packet_number: int):

        self.packet_number = packet_number

        self.__h = f"{packet_number:04},{int(checksum, 16):04}"
        self.__s = len(self.__h)

    def get(self):
        return self.__h.encode("utf-8")

    def size(self):
        return self.__s

    @classmethod
    def resolve(cls, pack: bytes):
        header = pack.decode()
        pack_num, checksum = header.split(",")
        return int(pack_num), int(checksum)

    def __str__(self):
        return self.__s


class Packet:
    """
        Represents a fragment of data.
        Contains header and payload, handles size and convertions.
    """

    def __init__(self, data_chunk: bytes, packet_number: int):

        self.packet_number = packet_number
        self.payload = data_chunk
        self.__header = Header(self.calc_checksum(self.payload), self.packet_number)

    def get(self):

        data_size = len(self.payload)
        assert (
            data_size + self.__header.size() <= MAX_PACK_SIZE
        ), f"Packet size exceeds maximum packet size. data: {data_size}, header: {self.__header.size()}"
        return self.__header.get() + self.payload

    @staticmethod
    def calc_checksum(data_chunk: bytes):
        return f"{(-(sum(data_chunk) % 256) & 0xFF):2x}"

    def check_checksum(self, checksum: int):

        pack_checksum = Packet.calc_checksum(self.payload)
        return int(pack_checksum, 16) == checksum

    @classmethod
    def resolve(cls, pack: bytes):
        pack_num, checksum = Header.resolve(pack[:HEADER_SIZE])
        data = pack[HEADER_SIZE:]
        packet = cls(data, pack_num)
        if packet.check_checksum(checksum):
            return packet
        else:
            return None

    def __str__(self):
        return f"{self.__header!s};[PAYLOAD[{len(self.payload)}]]"


def set_timeout(fn: Callable, timeout: int = 1, *args, **kwargs):
    """
        @param fn: The callable object to be executed after timeout.
        @param timeout: Amount of time before executing fn. In seconds.

        Adds delay to execution of function. Uses threading.Timer to achieve this.
    """
    t = Timer(timeout, fn, args=args, kwargs=kwargs)
    t.start()


class DataPackManager:
    """
        Manager class for data packets.
        Will be used to store coming data.  
    """

    def __init__(self):
        self.metadata_acquired = False
        self.__container = [None] * WINDOW_SIZE

    def allocate(self, packet_count: int):
        self.__container = [None for i in range(packet_count)]

    def received(self, packet: Packet):
        if packet.packet_number == 0:
            if self.metadata_acquired:
                return
 
            # metadata acquired
            self.metadata_acquired = True
            print('metadata acquired')
            try:
                packet_count = int.from_bytes(packet.payload, 'little')
                print(packet_count)
                current_count = len(self.__container)
                self.__container.extend([None] * (packet_count - current_count))
            except Exception as e:
                print(f'received : -> {e!r}')

        self.__container[packet.packet_number] = packet.payload

    @property
    def remaining(self):
        return next((True for _, x in enumerate(self.__container) if not x), False)

    @property
    def file(self):
        return b"".join(self.__container[1:])


class Ack(Packet):
    """
        Acknowledgement Packet.
    """

    def __init__(self, pack_num: int):
        super().__init__(ACKNOWLEDGED_MESSAGE, pack_num)


class Receiver:
    """
        Threading handler class.
    """

    # Queue for received packets
    received_packet_queue = Queue()

    # Data pack manager instance
    data_pack_manager = DataPackManager()

    # Interfaces that it should listen
    senders = list()
    # Interface that it should send acknowledgement
    ack_receivers = list()

    @staticmethod
    def listener(idx: int):
        """
            Listens socket and puts incoming packets to buffer(queue) 
        """
        interface = Receiver.senders[idx]
        fin = Packet(b"FINISHED", packet_number=-1)
        with UDP() as sock:

            sock.bind((interface, PORT))
            while True:
                pack = sock.recv(MAX_PACK_SIZE)
                if pack == b"":
                    break
                Receiver.received_packet_queue.put((pack, idx))
 
            fin_counter = 0
            sock.settimeout(TIMEOUT)
            while fin_counter < 5:
                for receiver in Receiver.ack_receivers:
                    sock.sendto(fin.get(), (receiver, PORT))
                try:
                    fin_ack = sock.recv(MAX_PACK_SIZE)
                except Exception as e:
                    print(f'{e!r}')
                    fin_counter += 1
                    continue
                if fin_ack == b'fin_ack':
                    break
        exit()
    @staticmethod
    def listen_worker():
        """
            Processes the packet by getting from buffer(queue)
        """
        with UDP() as sock:
            try:
                while Receiver.data_pack_manager.remaining:
                    # as long as missing packets remains
                    packet, idx = Receiver.received_packet_queue.get()
                    try:
                        packet = Packet.resolve(packet)
                    except Exception as e:
                        print(f" 223 => {e!r}")
                        continue
                    if packet:
                        # packet is accepted
                        Receiver.data_pack_manager.received(packet)
                        # return acknowledgement
                        ack_packet = Ack(packet.packet_number)
                        receiver = Receiver.ack_receivers[idx]
                        # send acknowledgement to corresponding link
                        sock.sendto(ack_packet.get(), (receiver, PORT))
                for sender in Receiver.senders:
                    # call listener to say we are going home
                    sock.sendto(b"", (sender, PORT))
            except Exception as e:
                print(f" 233 => {e!r}")



def conduct_experiment():
    """
        Conduct experiment
        starts threads, waits till they finishes
    """
    listen_worker = Thread(target=Receiver.listen_worker)
    listen_worker.start()
    listeners = [
        Thread(target=Receiver.listener, args=(idx,)) for idx, sender in enumerate(Receiver.senders)
    ]
    for listener in listeners:
        listener.start()

    for t in [listen_worker, *listeners]:
        t.join()


if __name__ == "__main__":

    if len(argv) == 1:
        experiment = 1
    else:
        experiment = argv[1]
    EXPERIMENT = int(experiment)
    if experiment == "1":
        Receiver.senders = [Interfaces.listen_router3]
        Receiver.ack_receivers = [Interfaces.send_router3]
    elif experiment == "2":
        Receiver.senders = [Interfaces.listen_router2, Interfaces.listen_router1]
        Receiver.ack_receivers = [Interfaces.send_router2, Interfaces.send_router1]
    conduct_experiment()
    with open(f"output{experiment}", "wb") as f:
        f.write(Receiver.data_pack_manager.file)
    """
    sudo tc qdisc change dev eth0 root netem loss 5% delay 3ms
    sudo tc qdisc change dev eth1 root netem loss 5% delay 3ms
    sudo tc qdisc change dev eth2 root netem loss 5% delay 3ms
    sudo tc qdisc change dev eth3 root netem loss 5% delay 3ms
    """