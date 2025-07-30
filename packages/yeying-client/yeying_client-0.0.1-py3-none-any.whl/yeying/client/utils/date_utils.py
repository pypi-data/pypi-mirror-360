from datetime import datetime, timedelta, timezone

from dateutil import parser
from dateutil import tz


def get_current_utc_datetime():
    return convert_to_utc_datetime(datetime.now())


def get_current_utc_string():
    return format_datetime(get_current_utc_datetime())


def get_current_iso_string():
    now_utc = datetime.now(timezone.utc)
    return now_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_datetime(s):
    return parser.isoparse(s)


def is_expired(s, minutes):
    # 解析ISO字符串
    time_parsed = parse_datetime(s)

    # 获取当前时间并保留时区信息
    now = datetime.now(time_parsed.tzinfo)

    # 计算5分钟之后的时间
    five_minutes_later = time_parsed + timedelta(minutes=minutes)

    # 比较时间，判断是否超过5分钟之后
    return now > five_minutes_later


def format_datetime(dt):
    formatted_dt = dt.isoformat(timespec="milliseconds")
    return formatted_dt.replace("+00:00", "Z")


def convert_to_local_datetime(dt):
    return dt.astimezone(tz.tzlocal())


def convert_to_utc_datetime(dt):
    return dt.astimezone(tz.tzutc())


def plus_second(dt: datetime, seconds: int) -> datetime:
    """
    向 datetime 对象添加指定的秒数

    :param dt: 原始 datetime 对象
    :param seconds: 要添加的秒数
    :return: 添加秒数后的新 datetime 对象

    >>> now = datetime.utcnow()
    >>> future = plus_second(now, 3600)  # 添加 1 小时（3600 秒）
    """
    return dt + timedelta(seconds=seconds)


def to_iso(dt: datetime) -> str:
    """
    将 datetime 对象转换为 ISO 8601 格式字符串

    :param dt: 要转换的 datetime 对象
    :return: ISO 8601 格式的字符串表示
    :example:
        now = datetime.now(timezone.utc)
        iso_str = to_iso(now)  # 返回 "2023-05-15T12:34:56.789+00:00"
    """
    # 确保 datetime 对象是带时区的
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # 转换为 ISO 格式字符串
    return dt.isoformat()


def from_iso(s: str) -> datetime:
    """
    从 ISO 字符串创建 datetime 对象

    :param s: ISO 8601 格式的日期字符串
    :return: 解析后的 datetime 对象
    :raises ValueError: 如果字符串无法解析则抛出错误
    :example:
        dt = from_iso("2023-05-15T12:34:56.789+00:00")
    """
    try:
        # 解析 ISO 格式字符串
        dt = datetime.fromisoformat(s)

        # 如果解析后的对象没有时区信息，添加 UTC 时区
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception as e:
        raise ValueError(f"无法解析 ISO 字符串: {s}") from e