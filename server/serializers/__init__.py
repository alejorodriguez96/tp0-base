"""Module for utility functions used by serializers and common functions."""
from enum import Enum

def get_agency_id_from_message(msg: bytes) -> int:
    """
    Extract the agency id from a message.
    """
    return int(msg[0])

class Separator(Enum):
    """
    Separator used to serialize/deserialize bets.
    """
    FIELD = b'\x1F'
    RECORD = b'\x1E'
