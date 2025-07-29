from typing import get_args, get_origin, Union

# On 3.10+ you can also detect the built-in union operator (A|B) via types.UnionType
try:
    from types import UnionType  # Python 3.10+
except ImportError:
    UnionType = None


def union_to_list(tp: type) -> list[type]:
    """
    If tp is a Union[X, Y, …] or X|Y|…, return [X, Y, …].
    Otherwise return [tp].
    """
    # Strips the TypeVar off the type. e.g. Union[int, str] -> Union
    origin = get_origin(tp)
    # classic typing.Union
    if origin is Union:
        # Returns the type arguments of the union. e.g. Union[int, str] -> [int, str]
        return list(get_args(tp))
    # PEP 604 union (only on 3.10+)
    if UnionType is not None and isinstance(tp, UnionType):
        # Returns the type arguments of the union. e.g. int | str -> [int, str]
        return list(get_args(tp))
    # not a union
    return [tp]
