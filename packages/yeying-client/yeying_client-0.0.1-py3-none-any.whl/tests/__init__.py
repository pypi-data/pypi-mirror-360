# -*- coding:utf-8 -*-
from yeying.client.utils import log_utils
import os
log = log_utils.get_logger(__name__)

current_dir = os.path.dirname(__file__)
print(current_dir)


id_file_path = os.path.join(current_dir, "id/tiger.id")
print(id_file_path)
test_file_path = os.path.join(current_dir, "data/test.txt")
print(test_file_path)

