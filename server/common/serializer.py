from enum import Enum
from common.utils import Bet
from common.errors import SerializationError

class Separator(Enum):
    """
    Separator used to serialize/deserialize bets.
    """
    FIELD = b'\x1F'
    RECORD = b'\x1E'

def deserialize_bet(data: bytes) -> Bet:
    """
    Deserialize a bet from a byte array.
    """
    try:
        fields = data.split(Separator.FIELD.value)
        return Bet(
            agency=int(fields[0]),
            first_name=fields[1].decode(),
            last_name=fields[2].decode(),
            document=fields[3].decode(),
            birthdate=fields[4].decode(),
            number=int(fields[5])
        )
    except Exception as e:
        raise SerializationError(f"Error while deserializing bet: {e}") from e

def deserialize_multiple_bets(data: bytes) -> list[Bet]:
    """
    Deserialize multiple bets from a byte array.
    """
    try:
        bets = []
        records = data.split(Separator.RECORD.value)
        for record in records:
            bets.append(deserialize_bet(record))
        return bets
    except Exception as e:
        raise SerializationError(f"Error while deserializing multiple bets: {e}") from e

def serialize_bet(bet: Bet) -> bytes:
    """
    Serialize a bet to a byte array.
    """
    try:
        barray = bytearray()
        barray.extend(str(bet.agency).encode())
        barray.append(Separator.FIELD.value)
        barray.extend(bet.first_name.encode())
        barray.append(Separator.FIELD.value)
        barray.extend(bet.last_name.encode())
        barray.append(Separator.FIELD.value)
        barray.extend(bet.document.encode())
        barray.append(Separator.FIELD.value)
        barray.extend(bet.birthdate.encode())
        barray.append(Separator.FIELD.value)
        barray.extend(str(bet.number).encode())
        return bytes(barray)
    except Exception as e:
        raise SerializationError(f"Error while serializing bet: {e}") from e

def serialize_multiple_bets(bets: list[Bet]) -> bytes:
    """
    Serialize multiple bets to a byte array.
    """
    try:
        barray = bytearray()
        for bet in bets:
            barray.extend(serialize_bet(bet))
            barray.append(Separator.RECORD.value)
        barray.pop()  # Remove last record separator
        return bytes(barray)
    except Exception as e:
        raise SerializationError(f"Error while serializing multiple bets: {e}") from e
