class ProtocolReceiveError(Exception):
    """Raised when a protocol error occurs."""
    def __init__(self, message):
        super().__init__(message)

class ProtocolSendError(Exception):
    """Raised when a protocol error occurs."""
    def __init__(self, message):
        super().__init__(message)

class SerializationError(Exception):
    """Raised when a Bet object cannot be serialized or deserialized."""
    def __init__(self, message):
        super().__init__(message)

class StorageError(Exception):
    """Raised when a bet cannot be stored or loaded from the storage file."""
    def __init__(self, message):
        super().__init__(message)

class CommunicationError(Exception):
    """Raised when a communication error occurs."""
    def __init__(self, message):
        super().__init__(message)
