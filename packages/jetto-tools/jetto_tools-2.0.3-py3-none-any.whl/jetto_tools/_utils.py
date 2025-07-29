from typing import Union

def is_int(string):
    try:
        int(string)
    except ValueError:
        return False
    return True

def is_float(string):
    try:
        float(string)
    except ValueError:
        return False
    return True

def is_bool(string):
    if string.lower() in ('true', 'false'):
        return True

    return False

def to_bool(string):
    if string.lower() == 'true':
        return True
    elif string.lower() == 'false':
        return False
    else:
        raise ValueError("String does not contain a boolean value")

def is_numeric(value) -> bool:
    """Check if a value is numeric

    A value is numeric if it is either of type int or float

    :param value: Object to check
    :return: True if the value is numeric; otherwise False
    :rtype: bool
    """
    return isinstance(value, int) or isinstance(value, float)

def to_numeric(value: str) -> Union[int, float]:
    """Convert a string to the appropriate numeric value

    Attempts to first convert the number to an integer: if that fails, it then tries conversion to a float. It returns
    the result of the first successful conversion

    :param value: String containing a numeric value
    :type value: str
    :return: Numeric value
    :rtype: int or float
    :raise: ValueError if the string cannot be parsed as a numeric value
    """
    try:
        n = int(value)
    except ValueError:
        pass
    else:
        return n

    return float(value)


