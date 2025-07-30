# -*- coding:utf-8 -*-
from yeying.api.common import DigitalFormatEnum


def get_ext_list_by_digital_format(digital_format: DigitalFormatEnum):
    cases = {
        DigitalFormatEnum.DIGITAL_FORMAT_IMAGE: [".jpg", "jpeg", ".gif", ".png", "webp"],
        DigitalFormatEnum.DIGITAL_FORMAT_VIDEO: [".mp4", ".avi", ".mov", ".flv"],
        DigitalFormatEnum.DIGITAL_FORMAT_AUDIO: [".mp3", ".wav", ".ogg"],
        DigitalFormatEnum.DIGITAL_FORMAT_TEXT: [".txt", ".csv", ".html", ".css"],
        DigitalFormatEnum.DIGITAL_FORMAT_APP: [".id", ".session", ".app", ".metadata", ".state", ".prompt"],
        DigitalFormatEnum.DIGITAL_FORMAT_OTHER: [],
    }
    return cases.get(digital_format, [])


def get_digital_format_by_name(name: str) -> DigitalFormatEnum:
    for digitalFormat in DigitalFormatEnum.values():
        res = next((item for item in get_ext_list_by_digital_format(digitalFormat) if name.endswith(item)), None)
        if res:
            return digitalFormat
    return DigitalFormatEnum.DIGITAL_FORMAT_OTHER
