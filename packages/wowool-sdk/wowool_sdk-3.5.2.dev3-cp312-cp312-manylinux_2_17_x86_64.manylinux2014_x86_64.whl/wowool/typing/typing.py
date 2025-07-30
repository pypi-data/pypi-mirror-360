from __future__ import annotations
import typing
import types


def is_typing_instance(typing_object, object_type) -> bool:
    """
    ex:
      typing_object = Optional[Union[str|int]]
      object_type   = str
    """
    if isinstance(typing_object, typing.TypeVar):
        for type_ in typing_object.__constraints__:
            if is_typing_instance(type_, object_type):
                return True
        return False
    else:
        origine_type = typing.get_origin(typing_object)
        if not origine_type:
            return typing_object is object_type
        if origine_type is typing.Union or origine_type is types.UnionType:
            args = typing.get_args(typing_object)
            for arg in args:
                if arg is object_type:
                    return True
                else:
                    other = typing.get_origin(arg)
                    if is_typing_instance(other, object_type):
                        return True
            return False
        elif origine_type:
            return origine_type is object_type
        else:
            return isinstance(typing_object, object_type)
