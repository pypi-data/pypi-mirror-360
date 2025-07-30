# -*- coding:utf-8 -*-
import logging

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # noqa
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def get_logger(name):
    return logging.getLogger(name)
