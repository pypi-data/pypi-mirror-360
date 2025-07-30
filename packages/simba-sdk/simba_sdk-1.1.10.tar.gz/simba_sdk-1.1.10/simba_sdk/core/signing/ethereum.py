from eth_account import Account
from eth_account.messages import encode_defunct

from simba_sdk.core.requests.client.credential import schemas as cs
from simba_sdk.core.signing import Signer


class EthereumSigner(Signer):
    def __init__(self, private_key):
        self._account = Account.from_key(private_key)
        super().__init__(self._account.address, private_key)

    def sign_transaction(self, pending_txn: cs.PendingTxn) -> cs.SignedTxn:
        if not isinstance(pending_txn, cs.PendingTxn):
            raise TypeError("pending_txn must be of type PendingTxn")
        signed = self._account.sign_transaction(pending_txn.raw_txn)
        signed_dict = signed._asdict()
        signed_dict["rawTransaction"] = signed_dict.pop(
            "raw_transaction"
        ).hex()  # There are some formatting differences that need sorting
        signed_dict["hash"] = signed_dict["hash"].hex()
        signed_txn = cs.SignedTxn(**signed_dict)
        return signed_txn

    def sign_message(self, message):
        if isinstance(message, bytes):
            signable_message = encode_defunct(primitive=message)
        elif isinstance(message, str):
            signable_message = encode_defunct(text=message)
        elif isinstance(message, int):
            signable_message = encode_defunct(hexstr=hex(message))
        else:
            raise TypeError("Message must be str, hexstr or bytes")
        return self._account.sign_message(signable_message)
