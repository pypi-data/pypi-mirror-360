"""
tcp_server.py
Written by: Joshua Kitchen - 2024
"""
import logging
import socket
import threading
import queue
import random
from typing import Generator

from .client_processor import ClientProcessor
from .tcp_client import TCPClient
from .message import Message

logger = logging.getLogger(__name__)


class TCPServer:
    """
    Creates, maintains, and transmits data to multiple TCP/IP connections.
    """

    def __init__(self, max_clients: int = 0, timeout: int = None):
        self._addr = (None, None)
        self._max_clients = max_clients
        self._timeout = timeout
        self._messages = queue.Queue()
        self._soc = None
        self._is_running = False
        self._is_running_lock = threading.Lock()
        self._connected_clients = {}
        self._connected_clients_lock = threading.Lock()

    @classmethod
    def from_socket(cls, soc: socket.socket, max_clients: int = 0) -> "TCPServer":
        """
        Allows for a server to be created from a socket object. The socket must be initialized and bound to an address.
        """
        out = cls(max_clients, soc.gettimeout())
        out._soc = soc
        out._addr = soc.getsockname()
        threading.Thread(target=out._mainloop).start()
        logger.info("Server has been started")
        return out

    @staticmethod
    def _generate_client_id() -> str:
        client_id = str(random.randint(0, 999999))
        client_id = int(client_id, base=36)
        return str(client_id)

    def _get_client(self, client_id: str) -> ClientProcessor:
        self._connected_clients_lock.acquire()
        try:
            client = self._connected_clients[client_id]
        except KeyError:
            self._connected_clients_lock.release()
            return
        self._connected_clients_lock.release()
        return client

    def _update_connected_clients(self, client_id: str, client: ClientProcessor):
        self._connected_clients_lock.acquire()
        self._connected_clients.update({client_id: client})
        self._connected_clients_lock.release()

    def _create_soc(self) -> bool:
        self._soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._soc.bind(self._addr)
        return

    def _mainloop(self):
        logger.debug("Server is listening for connections")
        self._set_is_running(True)
        while self._get_is_running():
            try:
                self._soc.listen()
                client_soc, client_addr = self._soc.accept()
                logger.info("Accepted Connection from %s @ %d", client_addr[0], client_addr[1])
                if self.is_full:
                    logger.warning("%s @ %d was denied connection due to server being full",
                                   client_addr[0], client_addr[1])
                    client_soc.close()
                    continue
                self._start_client_proc(self._generate_client_id(), client_soc)
            except ConnectionError:
                continue
            except TimeoutError:
                continue
            except AttributeError:  # Socket was closed from another thread
                self.stop()
                break
            except OSError:
                self.stop()
                break
        logger.debug("Server is no longer listening for messages")

    def _start_client_proc(self, client_id: str, client_soc: socket.socket):
        client = TCPClient.from_socket(client_soc)
        if not self.on_connect(client, client_id):
            client.disconnect()
            return
        client_proc = ClientProcessor(client_id=client_id,
                                      client_soc=client_soc,
                                      msg_q=self._messages,
                                      timeout=self._timeout)
        client_proc.start()
        self._update_connected_clients(client_proc.id, client_proc)

    def _get_is_running(self) -> bool:
        self._is_running_lock.acquire()
        running = self._is_running
        self._is_running_lock.release()
        return running

    def _set_is_running(self, value: bool):
        self._is_running_lock.acquire()
        self._is_running = value
        self._is_running_lock.release()

    def on_connect(self, client: TCPClient, client_id: str):
        """
        Override to control what actions the server will take when a new client connects.
        Returning False will disconnect the client.
        """
        return True

    @property
    def addr(self) -> tuple[str, int]:
        """
        Returns a tuple with the current address the server is listening on.
        """
        return self._addr

    @addr.setter
    def addr(self, value):
        return

    @property
    def is_running(self) -> bool:
        """
        Returns a boolean indicating whether the server is set up and running
        """
        return self._get_is_running()

    @is_running.setter
    def is_running(self, value):
        return

    @property
    def max_clients(self) -> int:
        """
        Returns an int representing the maximum allowed connections. Zero indicates that the server will allow infinite
        connections.
        """
        return self._max_clients

    @max_clients.setter
    def max_clients(self, new_max: int) -> int:
        """
        Sets the maximum number of allowed connections. The new_max argument should be a positive integer. Setting to
        zero will allow infinite connections.
        """
        if new_max < 0:
            raise ValueError("Value for max_clients should be a positive integer")
        self._max_clients = new_max

    @property
    def timeout(self):
        """
        Returns the timeout of the server's socket object used for listening for new connections
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: int):
        """
        Sets timeout (in seconds) of the server's socket object used for listening for new connections. The Timeout
        argument should be a positive integer. Passing None will set the timeout to infinity. See
        https://docs.python.org/3/library/socket.html#socket-timeouts for more information about timeouts.
        """
        if timeout is not None:
            if timeout < 0:
                raise ValueError("Value for timeout should be a positive integer")
        self._timeout = timeout
        self._soc.settimeout(timeout)

    @property
    def client_count(self) -> int:
        """
        Returns and int representing the number of connected clients
        """
        self._connected_clients_lock.acquire()
        count = len(self._connected_clients.keys())
        self._connected_clients_lock.release()
        return count

    @client_count.setter
    def client_count(self, value):
        return

    @property
    def is_full(self) -> bool:
        """
        Returns boolean flag indicating if the server is full
        """
        if self._max_clients > 0:
            if self.client_count == self._max_clients:
                return True
        return False

    @is_full.setter
    def is_full(self, value):
        return

    def set_clients_timeout(self, timeout: int) -> bool:
        """
        Sets the timeout (in seconds) of the all current client sockets. The Timeout argument should be a positive
        integer. Passing None will set the timeout to infinity. Returns True on success, False if not.
        See https://docs.python.org/3/library/socket.html#socket-timeouts for more information about timeouts.
        """
        if timeout is None:
            return
        elif timeout < 0:
            return
        for client_id in self.list_clients():
            client_proc = self._get_client(client_id)
            client_proc.timeout = timeout

    def list_clients(self) -> list:
        """
        Returns a list with the client ids of all connected clients
        """
        self._connected_clients_lock.acquire()
        client_list = self._connected_clients.keys()
        self._connected_clients_lock.release()
        return list(client_list)

    def get_client_info(self, client_id: str) -> dict:
        """
        Gives basic info about a client given a client_id.
        Returns a dictionary with keys 'is_running', 'timeout', 'addr'.
        Returns None if a client with client_id cannot be found
        """
        client = self._get_client(client_id)
        if not client:
            return
        return {
            "is_running": client.is_running,
            "timeout": client.timeout,
            "addr": client.remote_addr,
        }

    def disconnect_client(self, client_id: str) -> bool:
        """
        Disconnects a client with client_id. Returns False if no client with client_id was connected,
        True on a successful disconnect.
        """
        self._connected_clients_lock.acquire()
        try:
            client = self._connected_clients[client_id]
        except KeyError:
            self._connected_clients_lock.release()
            return False
        del self._connected_clients[client_id]
        self._connected_clients_lock.release()
        if client.is_running:
            client.stop()
        return True

    def pop_msg(self, block: bool = False, timeout: int = None) -> Message:
        """
        Get the next message in the queue. If block is True, this method will block until it can pop something from
        the queue, else it will try to get a value and return None if queue is empty. If block is True and a timeout
        is given, block until timeout expires and then return None if no item was received.
        See  https://docs.python.org/3/library/queue.html#queue.Queue.get for more information
        """
        try:
            return self._messages.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def get_all_msg(self, block: bool = False, timeout: int = None) -> Generator:
        """
        Generator for iterating over the message queue. If block is True, each iteration of this method will block until it
        can pop something from the queue, else it will try to get a value and yield None if queue is empty. If block
        is True and a timeout is given, block until timeout expires and then yield None if no item was received. See
        https://docs.python.org/3/library/queue.html#queue.Queue.get for more information
        """
        while not self._messages.empty():
            yield self.pop_msg(block=block, timeout=timeout)

    def has_messages(self) -> bool:
        """
        Returns a boolean indicating if the message queue has any messages
        """
        return not self._messages.empty()

    def send(self, client_id: str, data: bytes) -> bool:
        """
        Sends data to a connected client. Returns True on successful sending, False if not or if a client with
        client_id could not be found.
        """
        self._connected_clients_lock.acquire()
        try:
            client = self._connected_clients[client_id]
        except KeyError:
            self._connected_clients_lock.release()
            return False
        self._connected_clients_lock.release()
        return client.send(data)

    def start(self, addr: tuple[str, int]):
        """
        Starts the server and listens to the address provided.
        """

        if self._get_is_running():
            return
        self._addr = addr
        self._create_soc()
        threading.Thread(target=self._mainloop).start()
        logger.info("Server has been started")

    def stop(self):
        """
        Stops the server. If the server is not running, this method will do nothing.
        """
        if self._get_is_running():
            self._connected_clients_lock.acquire()
            for client in self._connected_clients.values():
                client.stop()
            self._connected_clients.clear()
            self._connected_clients_lock.release()
            self._soc.close()
            self._soc = None
            self._set_is_running(False)
            self._addr = (None, None)
            logger.info("Server has been stopped")
