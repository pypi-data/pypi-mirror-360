from yeying.client.model.exception import PermissionDeniedException, InvalidArgumentException
from yeying.client.model.identity import convert_did_to_publickey, encode_key
from yeying.client.utils.date_utils import get_current_utc_string, is_expired
from yeying.client.utils.object_utils import composite
from yeying.client.utils.signature_utils import verify, sign
from yeying.client.utils.string_utils import generate_uuid
from yeying.api.common import AuthenticateTypeEnum, MessageHeader
from yeying.api.web3 import BlockAddress


def verify_data(did: str, data: bytes, signature: str):
    if not verify(public_key=encode_key(convert_did_to_publickey(did)), data=data, signature=signature):
        raise PermissionDeniedException("Invalid signature!")


class Authenticate(object):
    def __init__(self, block_address: BlockAddress):
        self.block_address: BlockAddress = block_address
        self.validity = 5

    def get_did(self):
        return self.block_address.identifier

    def create_header(self, body=None):
        header = MessageHeader()
        header.did = self.block_address.identifier
        header.authType = AuthenticateTypeEnum.AUTHENTICATE_TYPE_CERT
        header.nonce = generate_uuid()
        header.version = 0
        header.timestamp = get_current_utc_string()

        if body is None:
            data = header.SerializeToString()
        else:
            data = composite(header.SerializeToString(), body.SerializeToString())

        header.authContent = self.sign_data(data)
        return header

    def verify_header(self, header, body=None):
        if is_expired(header.timestamp, self.validity):
            raise InvalidArgumentException("request expired!")

        signature = header.authContent
        header.authContent = ""
        if body is None:
            data = header.SerializeToString()
        else:
            data = composite(header.SerializeToString(), body.SerializeToString())

        verify_data(did=header.did, data=data, signature=signature)

    def sign_data(self, data: bytes):
        private_key = encode_key(self.block_address.privateKey)
        return sign(private_key, data)
