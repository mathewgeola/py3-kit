import re


def camel_to_snake(string: str) -> str:
    """
    >>> camel_to_snake("camelToSnake")
    'camel_to_snake'

    Args:
        string:

    Returns:

    """
    string = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    string = re.sub("([a-z0-9])([A-Z])", r"\1_\2", string).lower()
    return string


def snake_to_camel(string: str) -> str:
    """
    >>> snake_to_camel("snake_to_camel")
    'SnakeToCamel'

    Args:
        string:

    Returns:

    """
    return "".join(i.capitalize() for i in string.split("_"))
