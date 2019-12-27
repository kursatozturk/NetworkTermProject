from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from queue import Queue


UDP = lambda: socket(AF_INET, SOCK_DGRAM)

PORT = 23150
WHOAMI = "router3"


class Topology(type):
    """
        Topology class used in each node.
        Used python metaprogramming. 
        It returns corresponding ip according to WHOAMI variable
            and accessed attribute.
            i.e. if WHOMAI='source' and send_router3 is accessed
                then what is requested is the r3 interface of the link
                between s and r3. Returns router3_source
    """
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
        """
            Interfaces.send_router3 on source
                will return Topology.router3_source
        """
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
    """
        Interface to interfaces. uses Topology class as metaclass
            to achieve the use of __getattribute__ as intentend.
    """
    pass


MAX_PACK_SIZE = 1000


class Router:
    """
        Routing handler
    """

    # packet buffer
    packet_buffer = Queue()
    # acknowledgement buffer
    ack_buffer = Queue()

    @staticmethod
    def route_destination():
        """
            Routes packets came from source to destination
        """
        with UDP() as sock:
            while True:
                packet = Router.packet_buffer.get()
                if packet is None:
                    break
                sock.sendto(packet, (Interfaces.send_destination, PORT))

    @staticmethod
    def route_source():
        """
            Routes acknowledgements from destination to source
        """
        with UDP() as sock:
            while True:
                packet = Router.ack_buffer.get()
                if packet is None:
                    break
                sock.sendto(packet, (Interfaces.send_source, PORT))

    @staticmethod
    def listen_source():
        """
            Listens source and puts packets to queue
        """
        with UDP() as sock:
            sock.bind((Interfaces.listen_source, PORT))
            while True:
                pack = sock.recv(MAX_PACK_SIZE)
                Router.packet_buffer.put(pack)

    @staticmethod
    def listen_destination():
        """
            Listens destination to put acknowledgement to ack_queue
        """
        with UDP() as sock:
            sock.bind((Interfaces.listen_destination, PORT))
            while True:
                pack = sock.recv(MAX_PACK_SIZE)
                Router.ack_buffer.put(pack)


if __name__ == "__main__":
    """
        It is independent from experiment
    """
    route_source = Thread(target=Router.route_source)
    route_source.start()

    route_destination = Thread(target=Router.route_destination)
    route_destination.start()

    listen_source = Thread(target=Router.listen_source)
    listen_source.start()

    listen_destination = Thread(target=Router.listen_destination)
    listen_destination.start()

    for t in [route_source, route_destination, listen_source, listen_destination]:
        t.join()

