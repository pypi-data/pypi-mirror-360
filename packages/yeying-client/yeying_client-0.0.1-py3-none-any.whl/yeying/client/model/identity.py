import codecs
from yeying.client.utils.signature_utils import verify


def encode_key(key):
    return codecs.decode(key[2:] if key.startswith("0x") else key, "hex")


def convert_did_to_publickey(did):
    public_key = did.split(":")[-1]
    return public_key[2:] if public_key.startswith("0x") else public_key


def verify_identity(identity):
    signature = identity.signature
    try:
        identity.signature = ""
        public_key = encode_key(convert_did_to_publickey(identity.metadata.did))
        return verify(public_key=public_key, data=identity.SerializeToString(), signature=signature)
    finally:
        identity.signature = signature
