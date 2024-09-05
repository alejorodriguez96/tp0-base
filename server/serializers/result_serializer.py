"""Module for serializing/deserializing results."""
from model.bet import Bet
from serializers import Separator
from common.errors import SerializationError

def serialize_winners(winners_bets: list[Bet]) -> bytes:
    """
    Serialize the winners of a draw result.
    """
    try:
        barray = bytearray()
        for bet in winners_bets:
            barray.extend(bet.document.encode())
            barray.append(ord(Separator.RECORD.value))
        if barray:
            barray.pop()  # Remove the last separator
        return bytes(barray)
    except Exception as e:
        raise SerializationError(f"Error while serializing winners: {e}") from e
