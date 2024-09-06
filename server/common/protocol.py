import socket
from enum import Enum
from common.errors import ProtocolReceiveError, ProtocolSendError
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
    END = 0x05
    RESULT_REQUEST = 0x06
    RESULT = 0x07
    IN_PROGRESS = 0x08

def _byte_to_message_type(byte: bytes) -> MessageType:
    """
    Convert a byte to a MessageType
    """
    return MessageType(byte[0])

def receive(stream: BaseStream) -> tuple[MessageType, bytes]:
    """
    Read message from a specific client socket
    """
    try:
        # First we receive the 5 first bytes to know the type and length of the message
        header = stream.read(MESSAGE_TYPE_LEN + MESSAGE_LEN_LEN)
        msg_type = _byte_to_message_type(header[:MESSAGE_TYPE_LEN])
        msg_len = int.from_bytes(header[MESSAGE_TYPE_LEN:], byteorder='big')
        # Then we receive the rest of the message
        remaining = msg_len
        msg = stream.read(remaining)
    except Exception as e:
        raise ProtocolReceiveError("Error while receiving message") from e
    return msg_type, msg

def send(stream: BaseStream, msg: bytes, msg_type: MessageType):
    """
    Send a message to a specific client socket
    """
    try:
        # First we prepare the header
        header = bytearray()
        header.append(msg_type.value)
        header.extend(len(msg).to_bytes(MESSAGE_LEN_LEN, byteorder='big'))
        full_msg = header + msg
        # Then we send the full message
        stream.write(full_msg)
        return
    except Exception as e:
        raise ProtocolSendError("Error while sending message") from e
