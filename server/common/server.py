# pylint: disable=logging-fstring-interpolation
import socket
import logging
from multiprocessing import Pool, SimpleQueue, Array
import signal
from common import protocol, utils, errors
from serializers import bet_serializer, get_agency_id_from_message, result_serializer
from model.result import DrawResult
from common import storage_service, client_handler

class Server:
    """Class that represents a server that accepts connections and stores
    bets in a file"""
    def __init__(self, port, listen_backlog, clients_amount):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._keep_running = True
        self._clients_amount = clients_amount

        self._clients_finished = Array('i', clients_amount)
        self._storer_queue = SimpleQueue()
        self._handlers = []

        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, _signo, _stack_frame):
        logging.debug("Server is shutting down")
        self._keep_running = False
        self._server_socket.close()
        for handler in self._handlers:
            handler.terminate()
        for handler in self._handlers:
            handler.join()
        self._storer_queue.put((storage_service.StorageServiceMessages.STOP, None))
        self._storer_queue.close()
        logging.debug("Server has shut down")

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        storer_process = storage_service.StorageService(self._storer_queue)
        storer_process.start()

        while self._keep_running:
            try:
                client_sock = self.__accept_new_connection()
                handler = client_handler.ClientHandler(
                    client_sock,
                    self._storer_queue,
                    self._clients_finished,
                    self._clients_amount
                )
                handler.start()
                self._handlers.append(handler)
            except OSError as e:
                logging.error(f"action: accept_connections | result: fail | error: {e}")
                client_sock.close()
                self._server_socket.close()

    

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
