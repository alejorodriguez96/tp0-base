from enum import Enum
from common.errors import ProtocolReceiveError, ProtocolSendError, CommunicationError
from common.communication import BaseStream

MESSAGE_TYPE_LEN = 1
MESSAGE_LEN_LEN = 4

class MessageType(Enum):
    """
    Message types used in the protocol.
    """
    BET = 0x01
    MULTIPLE_BETS = 0x02
    ERROR = 0x03
    BET_ACK = 0x04

def _byte_to_message_type(byte: bytes) -> MessageType:
    """
    Convert a byte to a MessageType
    """
    return MessageType(byte[0])


def receive(stream: BaseStream) -> tuple[MessageType, bytes]:
    """
    Read raw message from a stream and return the message type and the message itself.
    """
    try:
        # First we receive the 5 first bytes to know the type and length of the message
        header = stream.read(MESSAGE_TYPE_LEN + MESSAGE_LEN_LEN)
        msg_type = _byte_to_message_type(header[:MESSAGE_TYPE_LEN])
        msg_len = int.from_bytes(header[MESSAGE_TYPE_LEN:], byteorder='big')
        # Then we receive the rest of the message
        msg = stream.read(msg_len)
    except CommunicationError as e:
        raise ProtocolReceiveError(f"Error while receiving message: {e}") from e
    return msg_type, msg

def send(stream: BaseStream, msg: bytes, msg_type: MessageType):
    """
    Given a message and its type, build the corresponding header and send the message
    to the stream.
    """
    try:
        # First we prepare the header
        header = bytearray()
        header.append(msg_type.value)
        header.extend(len(msg).to_bytes(MESSAGE_LEN_LEN, byteorder='big'))
        full_msg = header + msg
        stream.write(full_msg)
    except Exception as e:
        raise ProtocolSendError(f"Error while sending message: {e}") from e
