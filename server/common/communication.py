"""Module containing classes for communication between server and client"""
import socket
from common.errors import CommunicationError

class BaseStream:
    """Abstract class for reading data"""
    def read(self, _size: int) -> bytes:
        """Read size bytes from the reader"""
        raise NotImplementedError

    def write(self, _data: bytes):
        """Write data to the reader"""
        raise NotImplementedError

class SocketStream(BaseStream):
    """Class for reading data from a socket"""
    def __init__(self, sock: socket.socket):
        self.sock = sock

    def read(self, size: int) -> bytes:
        try:
            remaining = size
            data = bytearray()
            while remaining > 0:
                chunk = self.sock.recv(remaining)
                data.extend(chunk)
                remaining -= len(chunk)
            return bytes(data)
        except socket.error as e:
            raise CommunicationError(f"Error receiving data: {e}") from e

    def write(self, data: bytes):
        try:
            remaining = len(data)
            while remaining > 0:
                sent = self.sock.send(data)
                remaining -= sent
        except socket.error as e:
            raise CommunicationError(f"Error sending data: {e}") from e
