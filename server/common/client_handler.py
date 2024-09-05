# pylint: disable=logging-fstring-interpolation
from typing import Any
from multiprocessing import Process, SimpleQueue, Pipe
from socket import socket
import logging
from common import protocol, utils, errors
from serializers import bet_serializer, get_agency_id_from_message, result_serializer
from model.result import DrawResult
from common.storage_service import StorageServiceMessages

class ClientHandler(Process):

    def __init__(
        self,
        client_sock: socket,
        storage_queue: SimpleQueue,
        clients_finished: Any,
        clients_amount: int
    ):
        """
        Initialize the client handler process

        Function that initializes the client handler process
        """
        Process.__init__(self)
        self._client_sock = client_sock
        self._storage_queue = storage_queue
        self._clients_finished = clients_finished
        self._clients_amount = clients_amount

    def terminate(self):
        """
        Terminate the client handler process

        Function that terminates the client handler process
        """
        self._client_sock.close()
        Process.terminate(self)

    def run(self):
        """
        Run the client handler process

        Function that runs the client handler process. It will
        receive messages from the client socket and process them
        """
        try:
            msg_type, msg = protocol.receive(self._client_sock)
            logging.info(f"Message type: {msg_type}")
            if msg_type == protocol.MessageType.BET:
                self.__handle_bet_message(self._client_sock, msg)
            elif msg_type == protocol.MessageType.MULTIPLE_BETS:
                self.__handle_multiple_bets_message(self._client_sock, msg)
            elif msg_type == protocol.MessageType.END:
                self.__handle_end_message(msg)
            elif msg_type == protocol.MessageType.RESULT_REQUEST:
                self.__handle_result_request(self._client_sock, msg)
        except errors.ProtocolReceiveError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self._client_sock.close()

    def __handle_end_message(self, msg):
        """
        Handle an end message
        """
        agency_id = get_agency_id_from_message(msg)
        logging.info(f"action: end_message | result: success | agency_id: {agency_id}")
        self._clients_finished[agency_id - 1] = True


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
            clients_finished = [c for c in self._clients_finished[:] if c]
            if len(clients_finished) == self._clients_amount:
                bets = self._load_bets()
                result = DrawResult.from_bet_list(bets)
                msg = result_serializer.serialize_winners(result.get_winners_from_agency(agency_id))
                protocol.send(client_sock, msg, protocol.MessageType.RESULT)
                logging.info(f"action: result_request | result: success | agency_id: {agency_id}")
            else:
                protocol.send(client_sock, b'', protocol.MessageType.IN_PROGRESS)
                logging.info(f"action: result_request | result: in_progress | agency_id: {agency_id}")
        except (
            errors.ProtocolSendError,
            OSError
         ) as e:
            logging.error(f"action: result_request | result: fail | error: {e}")

    def __handle_bet_message(self, client_sock, msg):
        """
        Handle a bet message

        Function receives a message from a client socket and
        processes it. Then, a response is sent to the client
        """
        try:
            bet = bet_serializer.deserialize_bet(msg)
            self._store_bets([bet])
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
            self._store_bets(bets)
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

    def _load_bets(self):
        """
        Communicate with the storage service to load the bets
        """
        try:
            recv_pipe, send_pipe = Pipe(duplex=False)
            self._storage_queue.put((StorageServiceMessages.GET_BETS, send_pipe))
            bets = recv_pipe.recv()
        except Exception as e:
            recv_pipe.close()
            raise e
        return bets

    def _store_bets(self, bets):
        """
        Communicate with the storage service to store the bets
        """
        try:
            recv_pipe, send_pipe = Pipe(duplex=False)
            self._storage_queue.put((StorageServiceMessages.STORE_BETS, (bets, send_pipe)))
            response = recv_pipe.recv()
            if not response:
                raise errors.StorageError("Error storing bets")
        except Exception as e:
            recv_pipe.close()
            raise e
