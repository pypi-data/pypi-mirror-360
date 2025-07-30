import abc
from typing import Dict, Union


class Signer(abc.ABC):
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

    @abc.abstractmethod
    def sign_transaction(self, txn_data: Dict):
        pass

    @abc.abstractmethod
    def sign_message(self, data: Union[str, bytes]):
        pass
