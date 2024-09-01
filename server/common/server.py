import socket
import logging
import signal
from common import protocol, serializer, utils, errors


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._keep_running = True
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, _signo, _stack_frame):
        logging.debug("Server is shutting down")
        self._keep_running = False
        self._server_socket.close()

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._keep_running:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError as e:
                logging.error(f"action: accept_connections | result: fail | error: {e}")
                client_sock.close()
                self._server_socket.close()

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = protocol.receive(client_sock)
            logging.info(f"action: receive_message | result: success | msg: {msg}")
            bet = serializer.deserialize_bet(msg)
            utils.store_bets([bet])
            logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")
            protocol.send(client_sock, b'OK', protocol.MessageType.BET_ACK)
            logging.info(f"action: send_message | result: success | msg: OK")
        except errors.ProtocolReceiveError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        except errors.SerializationError as e:
            logging.error(f"action: apuesta_almacenada | result: fail | error: {e}")
        except errors.StorageError as e:
            logging.error(f"action: apuesta_almacenada | result: fail | error: {e}")
        except errors.ProtocolSendError as e:
            logging.error(f"action: send_message | result: fail | error: {e}")
        finally:
            client_sock.close()

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
