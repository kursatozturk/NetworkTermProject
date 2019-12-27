from socket import socket, AF_INET, SOCK_DGRAM
from ipaddress import IPv4Address
from threading import Timer, Thread, Lock
from queue import Queue
from typing import Callable, Optional, List
from functools import wraps
from sys import argv
from functools import reduce

UDP = lambda: socket(AF_INET, SOCK_DGRAM)

PORT = 23150

TIMEOUT = 0.3

MAX_PACK_SIZE = 1000
HEADER_SIZE = 9
PAYLOAD_SIZE = MAX_PACK_SIZE - HEADER_SIZE

WINDOW_SIZE = 32

WHOAMI = "source"


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
        """
            @param checksum: calculated checksum of payload. It is inserted into header to detect data corruption. must be str of int.
            @param packet_number: packet number
        """
        self.packet_number = packet_number
        self.__h = f"{packet_number:04},{int(checksum, 16):04}"
        self.__s = len(self.__h)

    def get(self) -> bytes:
        """
            Returns bytes representation of header.
        """
        return self.__h.encode("utf-8")

    def size(self) -> int:
        """
            Size of header. 
            It must always equal to HEADER_SIZE
        """
        return self.__s

    @classmethod
    def resolve(cls, pack: bytes):
        """
            Resolves Header from bytes.
            Returns packet number and checksum.
            @param pack: bytes object that to be resolved.
        """
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

    def __init__(self, payload: bytes, packet_number: int):
        """
            @param payload: payload to be sent to destination. must be bytes type.
            @param packet_number: packet number is used for ordering and packet loss detection. must be int type. 
        """
        self.packet_number = packet_number
        self.payload = payload
        self.__header = Header(self.calc_checksum(self.payload), self.packet_number)
        assert len(self.payload) + self.__header.size()

    def get(self) -> bytes:
        """
           Return bytes representation of packet. 
           Includes header and payload. 
        """

        data_size = len(self.payload)
        assert (
            data_size + self.__header.size() <= MAX_PACK_SIZE
        ), f"Packet size exceeds maximum packet size. data: {data_size}, header: {self.__header.size()}"
        return self.__header.get() + self.payload

    @staticmethod
    def calc_checksum(data_chunk: bytes) -> str:
        """
            Calculates checksum of bytes object.
            @param data_chunk: bytes object whom checksum be calculated.
            @returns string represantation of checksum in hex.
        """
        return f"{(-(sum(data_chunk) % 256) & 0xFF):2x}"

    def check_checksum(self, checksum: int) -> bool:
        """
            Calculates its checksum and checks if it is equal to given checksum.
            @param checksum: required checksum
        """
        pack_checksum = Packet.calc_checksum(self.payload)
        return int(pack_checksum, 16) == checksum

    @classmethod
    def resolve(cls, pack: bytes) -> Optional[int]:
        """
            Resolves packet from bytes object.
            Checks checksum of payload.
            If packet is valid, returns packet number.
            @param pack: bytes object to be resolved
        """
        pack_num, checksum = Header.resolve(pack[:HEADER_SIZE])
        data = pack[HEADER_SIZE:]
        packet = cls(data, pack_num)
        if packet.check_checksum(checksum):
            return pack_num
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
        Used for packet controlling, i.e. caches packets till packets acknowledged,
        control window operations such as checking window is sent, window size etc.
    """

    def __init__(self):

        self.__container = []
        self.__window_index = 0

    def add_packet(self, packet: Packet):
        """
            adds packet to cache.
            @param packet: Packet object to be cached.
        """
        self.__container.append(packet)

    @property
    def packet_count(self):
        """
            count of packets
        """
        return len(self.__container)

    @property
    def packets(self) -> List[Packet]:
        """
            packets
        """
        return self.__container

    @property
    def remaining(self) -> int:
        """
            Returns count of remaining packets. i.e. not yet acknowledged.
        """
        remaining = sum(x is not None for x in self.packets)
        return remaining

    @property
    def window_index(self) -> int:
        return self.__window_index

    def next_window(self):
        """
            slides window by WINDOW_SIZE.
        """
        self.__window_index += WINDOW_SIZE

    @property
    def window_sent(self) -> bool:
        """
            returns if current window is fully sent and checked
        """
        window_index = self.__window_index
        return reduce(
            lambda x, y: x and not y,
            self.packets[window_index : window_index + WINDOW_SIZE],
            True,
        )

    def acknowledged(self, pack_num: int):
        """
            deletes acknowledged packet from cache
        """
        if pack_num == -1:
            print("Meta data acknowledgement should've not been come to here")
            return
        self.__container[pack_num] = None

    def get(self, pack_num: int) -> Optional[Packet]:
        """
            return packet having given packet number
        """
        if len(self.__container) <= pack_num:
            print(
                f"Cannot resend not known package! Max packet number: {len(self.__container)}; received acknowledgment for {pack_num}"
            )
            return None
        return self.__container[pack_num]


class Sender:
    """
        Threading Manager
    """

    # Acknowledgement packets are put in this queue
    ack_queue = Queue()

    # Resend required packets are put in this queue
    resend_queue = Queue()

    # Packet Manager instance
    pack_manager = DataPackManager()

    # Lock object for window sliding.
    window_lock = Lock()

    # Lock to be used in metadata sending
    metadata_lock = Lock()

    # set of receivers
    # will be fed in main thread according to command line parameters
    receivers = set()

    # set of acknowledgement listener interface
    # will be fed in main thread according to command line parameters
    ack_listeners = set()

    @staticmethod
    def send_data(file_path: str = "./input.txt"):
        """
            Thread entry function for sending data.
            Sends data to router links specified in Sender.receivers
        """
        # acquire lock to block in first acquire
        # Sender.window_lock.acquire()

        with open(file_path, "rb") as f:
            while True:
                data_chunk = f.read(PAYLOAD_SIZE)
                if not data_chunk:
                    break

                pack_num = Sender.pack_manager.packet_count
                packet = Packet(data_chunk, pack_num)
                Sender.pack_manager.add_packet(packet)
        with UDP() as sock:
            # send metadata to destination
            # so it alloctes memory for upcoming file
            print("acquires metadata_lock")
            Sender.metadata_lock.acquire()
            while True:

                for receiver in Sender.receivers:
                    sock.sendto(
                        Sender.pack_manager.packet_count.to_bytes(8, "little"),
                        (receiver, PORT),
                    )
                try:
                    print("acquire to exit")
                    Sender.metadata_lock.acquire(timeout=TIMEOUT)
                    break
                except TimeoutError:
                    print("TimeOut. Resending metadata")
                    # resend metadata again
                    pass
                except Exception as e:
                    print(e)
                    pass

            packets = Sender.pack_manager.packets
            while Sender.pack_manager.remaining:
                Sender.window_lock.acquire()
                first_packet = Sender.pack_manager.window_index
                last_packet = first_packet + WINDOW_SIZE
                print(f"sending packets: [{first_packet}, {last_packet}]")
                for packet in packets[first_packet:last_packet]:
                    for receiver in Sender.receivers:
                        """
                            Ack for metadata may be causing last element to be zero,
                        """
                        sock.sendto(packet.get(), (receiver, PORT))

                    set_timeout(
                        Sender.resend_pack,
                        timeout=TIMEOUT,
                        pack_num=packet.packet_number,
                    )
        # inform resend thread that we are going home
        Sender.resend_queue.put(None)

    @staticmethod
    def resend_pack(pack_num: int):
        packet = Sender.pack_manager.get(pack_num)
        if packet:
            Sender.resend_queue.put(packet)

    @staticmethod
    def listen_ack(listen_interface: str):
        """
            Listens and puts each packet received for workers to queue. 
        """
        with UDP() as sock:
            sock.bind((listen_interface, PORT))
            while True:
                packet = sock.recv(MAX_PACK_SIZE)
                if packet == b"":
                    break
                Sender.ack_queue.put(packet)
        print("Acknowledgement listening exitting")

    @staticmethod
    def listen_worker():
        """
            Will work till None put to ack_queue
        """
        metadata = None
        while metadata != -1:
            metadata_ack = Sender.ack_queue.get()
            metadata = Packet.resolve(metadata_ack)
            print("metadata must be acknowledged")
        Sender.metadata_lock.release()
        while True:
            # get packet from queue
            pack = Sender.ack_queue.get()
            # resolve it
            pack_num = Packet.resolve(pack)
            if pack_num is not None:
                # if it is valid, acknowledge it
                Sender.pack_manager.acknowledged(pack_num)
                if Sender.pack_manager.window_sent:
                    # if window is sent, slide window
                    Sender.pack_manager.next_window()
                    # inform sender thread that window is slided
                    Sender.window_lock.release()

                if not Sender.pack_manager.remaining:
                    # if all packets are sent, terminate safely.
                    with UDP() as sock:
                        print("Sending empty message to ack listen thread.")
                        for ack_listener in Sender.ack_listeners:
                            sock.sendto(b"", (ack_listener, PORT))
                    break

        print("Listen Worker exits")

    @staticmethod
    def resend_worker():
        """
            Will work till None put to resend_queue
        """
        with UDP() as sock:
            while True:
                # get packet from queue
                packet: Packet = Sender.resend_queue.get()
                if packet is None:
                    # stop signal
                    break
                for receiver in Sender.receivers:
                    # send to all available links
                    sock.sendto(packet.get(), (receiver, PORT))
                # set timeout again
                set_timeout(
                    Sender.resend_pack, timeout=TIMEOUT, pack_num=packet.packet_number
                )


def conduct_experiment():
    """
        Sender.receivers and sender.ack_listeners must be set before this function invoked.
    """
    assert Sender.receivers
    assert Sender.ack_listeners

    listen_ack_threads = [
        Thread(target=Sender.listen_ack, args=(listener,))
        for listener in Sender.ack_listeners
    ]
    listen_worker_thread = Thread(target=Sender.listen_worker)
    listen_worker_thread.start()
    for listen_ack_thread in listen_ack_threads:
        listen_ack_thread.start()
    resend_worker_thread = Thread(target=Sender.resend_worker)
    resend_worker_thread.start()
    send_thread = Thread(target=Sender.send_data)
    send_thread.start()
    for t in [
        *listen_ack_threads,
        listen_worker_thread,
        resend_worker_thread,
        send_thread,
    ]:
        t.join()


def experiment1_settings():
    Sender.receivers = {Interfaces.send_router3}
    Sender.ack_listeners = {Interfaces.listen_router3}


def experiment2_settings():
    Sender.receivers = {Interfaces.send_router2, Interfaces.send_router1}
    Sender.ack_listeners = {
        Interfaces.listen_router2,
        Interfaces.listen_router1,
    }


if __name__ == "__main__":
    if len(argv) == 1:
        experiment = 1
    else:
        experiment = argv[1]
    if experiment == "1":
        experiment1_settings()
    elif experiment == "2":
        experiment2_settings()
    else:
        raise ValueError("Experiment must be either 1, 2 or not preset")
    conduct_experiment()
