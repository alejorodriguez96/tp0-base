from multiprocessing import Process, SimpleQueue, Pipe
from multiprocessing.connection import Connection
from enum import Enum
from common.utils import store_bets, load_bets

class StorageServiceMessages(Enum):
    STOP = 0
    STORE_BETS = 1
    GET_BETS = 2

class StorageService(Process):
    def __init__(self, queue: SimpleQueue):
        Process.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                data, payload = self.queue.get()
                if data == StorageServiceMessages.STOP:
                    break
                elif data == StorageServiceMessages.STORE_BETS:
                    bets, response_pipe = payload
                    self._store_bets(bets, response_pipe)
                elif data == StorageServiceMessages.GET_BETS:
                    self._load_bets(payload)
            except Exception as e:
                print(f"Error: {e}")

    def _store_bets(self, bets, response_pipe):
        try:
            store_bets(bets)
            response_pipe.send(True)
        except Exception as e:
            response_pipe.send(False)
            response_pipe.close()
            raise e

    def _load_bets(self, response_pipe):
        try:
            response_pipe.send(list(load_bets()))
        except Exception as e:
            response_pipe.close()
            raise e
