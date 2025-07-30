# -*- coding:utf-8 -*-
import os

from tests import id_file_path
from yeying.api.web3 import Identity
from yeying.client.model.option import ProviderOption
from yeying.client.tool.identity_service import load, decrypt_block_address

identity_file = id_file_path
if not os.path.exists(identity_file):
    raise Exception(f"identity_file not exists {identity_file}")

identity: Identity = load(identity_file)
block_address = decrypt_block_address(identity.blockAddress, identity.securityConfig.algorithm, "123456")
print(f"block_address={block_address}")
proxy = os.environ.get("WAREHOUSE_ENDPOINT", "http://localhost:8641")
option: ProviderOption = ProviderOption(proxy=proxy, block_address=block_address)