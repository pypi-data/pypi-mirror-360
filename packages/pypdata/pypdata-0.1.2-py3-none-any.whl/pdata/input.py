import datetime

from typing import Optional

from .time_util import LOCAL_TIME_OFFSET, utc_timestamp


__all__ = [
    'DateTimeArgType',
    'StrListArgType',
    'parse_datetime_arg',
    'parse_datetime_arg_utc',
    'parse_str_list_arg',
]


StrListArgType = Optional[str | list[str]]

def parse_str_list_arg(arg: StrListArgType) -> list[str]:
    """
    Parse a string or a list of strings into a list of strings.

    If the input is None, an empty list is returned.
    If the input is a single string, it is split by commas and stripped of whitespace.
    If the input is already a list, it is returned as is.

    Args:
        arg (StrListArgType): The input argument to parse.

    Returns:
        list[str]: A list of strings.
    """
    if arg is None:
        return []
    if isinstance(arg, str):
        if not arg.strip():
            return []
        return [s.strip() for s in arg.split(',')]
    return [s.strip() for s in arg]


DateTimeArgType = Optional[datetime.date | datetime.datetime | str | int]

def parse_datetime_arg_utc(arg: DateTimeArgType, default_now: bool = True) -> int:
    """
    Parse a date, datetime, string, or integer into a Unix timestamp.

    If the input is None and default_now is True, the current time is used.
    If the input is a string, it is parsed as an ISO 8601 date/time.
    If the input is an integer, it is assumed to be a Unix timestamp.

    Args:
        arg (DateTimeArgType): The input argument to parse.
        default_now (bool): Whether to use the current time if arg is None.

    Returns:
        int: The Unix timestamp in milliseconds.
    """
    if arg is None:
        if default_now:
            return int(datetime.datetime.now().timestamp() * 1000)
        return 0

    if isinstance(arg, int):
        return arg

    if not isinstance(arg, (datetime.date, datetime.datetime, str)):
        raise TypeError(f"Unsupported type for datetime argument: {type(arg)}")

    if isinstance(arg, str):
        if len(arg) == 8:   # YYYYMMDD
            dt = datetime.datetime.strptime(arg, '%Y%m%d')
        elif len(arg) == 10:  # YYYY-MM-DD
            dt = datetime.datetime.strptime(arg, '%Y-%m-%d')
        elif len(arg) == 19:  # YYYY-MM-DD HH:MM:SS
            dt = datetime.datetime.strptime(arg, '%Y-%m-%d %H:%M:%S')
        elif len(arg) == 20 and arg[19] == 'Z':  # YYYY-MM-DDTHH:MM:SSZ
            dt = datetime.datetime.strptime(arg[:-1], '%Y-%m-%dT%H:%M:%S')
        else:
            raise TypeError(f"Unsupported datetime format: {arg}")
    else:
        dt = arg

    return utc_timestamp(dt)


def parse_datetime_arg(arg: DateTimeArgType, use_local: bool = False, default_now: bool = True) -> int:
    """
    Parse a date, datetime, string, or integer into a Unix timestamp.

    If the input is None and default_now is True, the current time is used.
    If use_local is True, the local timezone is used; otherwise, UTC is used.

    Args:
        arg (DateTimeArgType): The input argument to parse.
        use_local (bool): Whether to use the local timezone. If arg is an integer or a date, this is ignored.
        default_now (bool): Whether to use the current time if arg is None.

    Returns:
        int: The Unix timestamp in milliseconds.
    """
    if isinstance(arg, int):
        return arg

    res = parse_datetime_arg_utc(arg, default_now)

    if arg is None:
        use_local = False
    if isinstance(arg, datetime.date):
        use_local = False
    elif isinstance(arg, str) and (len(arg) in (8, 10) or arg.endswith('Z')):
        use_local = False

    if use_local:
        return res - LOCAL_TIME_OFFSET
    return res


ParamArgType = Optional[str | dict[str, str | list[str]]]

def parse_param_arg(arg: ParamArgType) -> dict[str, list[str]]:
    """
    Parse a parameter argument into a dictionary.

    If the input is None, an empty dictionary is returned.
    If the input is a string, it is split by semicolon, value split by commas, and stripped of whitespace.
    If the input is a dictionary, it is processed to ensure all values are lists.

    Args:
        arg (ParamArgType): The input argument to parse.

    Returns:
        dict[str, list[str]]: A dictionary with string keys and list of strings as values.
    """
    if arg is None:
        return {}

    if isinstance(arg, str):
        arg = arg.strip()
        if not arg:
            return {}

        res = {}
        for arg_split in arg.split(';'):
            if '=' not in arg_split:
                raise ValueError(f"Invalid param argument: {arg_split}")
            k, v = arg_split.split('=', 1)
            k = k.strip()
            v = v.strip()
            if not k or not v:
                continue
            res[k] = parse_str_list_arg(v)
        return res

    if not isinstance(arg, dict):
        raise TypeError(f"Unsupported type for param argument: {type(arg)}")

    res = {}
    for k, v in arg.items():
        if not isinstance(v, (str, list)):
            v = str(v)

        if isinstance(v, str):
            res[k.strip()] = [v]
        else:
            res[k.strip()] = [str(s) for s in v]
    return res
