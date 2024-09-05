# pylint: disable=logging-fstring-interpolation
import socket
import logging
import signal
from common import protocol, utils, errors
from serializers import bet_serializer, get_agency_id_from_message, result_serializer
from model.result import DrawResult

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
        self._clients_finished = set()
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
        close_at_end = True
        try:
            msg_type, msg = protocol.receive(client_sock)
            logging.info(f"Message type: {msg_type}")
            if msg_type == protocol.MessageType.BET:
                self.__handle_bet_message(client_sock, msg)
            elif msg_type == protocol.MessageType.MULTIPLE_BETS:
                self.__handle_multiple_bets_message(client_sock, msg)
            elif msg_type == protocol.MessageType.END:
                self.__handle_end_message(msg)
            elif msg_type == protocol.MessageType.RESULT_REQUEST:
                close_at_end = False
                self.__handle_result_request(client_sock, msg)
        except errors.ProtocolReceiveError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            if close_at_end:
                client_sock.close()


    def __handle_end_message(self, msg):
        """
        Handle an end message
        """
        agency_id = get_agency_id_from_message(msg)
        logging.info(f"action: end_message | result: success | agency_id: {agency_id}")
        self._clients_finished.add(agency_id)


    def __handle_result_request(self, client_sock, msg):
        """
        Handle a result request message

        Function receives a message from a client socket and
        processes it. Then, a response might be sent to the client if all the
        clients have already sent their bets, otherwise the server will
        queue the client socket to send the result later
        """
        agency_id = get_agency_id_from_message(msg)
        try:
            if len(self._clients_finished) == self._clients_amount:
                bets = utils.load_bets()
                result = DrawResult.from_bet_list(bets)
                msg = result_serializer.serialize_winners(result.get_winners_from_agency(agency_id))
                protocol.send(client_sock, msg, protocol.MessageType.RESULT)
                logging.info(f"action: result_request | result: success | agency_id: {agency_id}")
            else:
                protocol.send(client_sock, b'', protocol.MessageType.IN_PROGRESS)
                logging.info(f"action: result_request | result: in_progress | agency_id: {agency_id}")
        except errors.ProtocolSendError as e:
            logging.error(f"action: result_request | result: fail | error: {e}")

    def __handle_bet_message(self, client_sock, msg):
        """
        Handle a bet message

        Function receives a message from a client socket and
        processes it. Then, a response is sent to the client
        """
        try:
            bet = bet_serializer.deserialize_bet(msg)
            utils.store_bets([bet])
            logging.info(
                "action: apuesta_almacenada | result: success "
                f"| dni: {bet.document} | numero: {bet.number}"
            )
            protocol.send(client_sock, b'OK', protocol.MessageType.BET_ACK)
        except (
            errors.SerializationError,
            errors.StorageError,
            errors.ProtocolReceiveError
        ) as e:
            logging.error(f"action: apuesta_almacenada | result: fail | error: {e}")
            

    def __handle_multiple_bets_message(self, client_sock, msg):
        """
        Handle a multiple bets message

        Function receives a message from a client socket and
        processes it. Then, a response is sent to the client
        """
        try:
            bets = bet_serializer.deserialize_multiple_bets(msg)
            utils.store_bets(bets)
            logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
            protocol.send(client_sock, b'OK', protocol.MessageType.BET_ACK)
            logging.info("action: send_message | result: success | msg: OK")
        except (
            errors.SerializationError,
            errors.StorageError,
            errors.ProtocolReceiveError,
            OSError
        ) as e:
            try:
                logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
            except NameError:
                logging.error(f"action: apuesta_recibida | result: fail | cantidad: {e}")
            protocol.send(client_sock, b'ERROR', protocol.MessageType.ERROR)

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
