from dataclasses import fields
from typing import Type


def parse(dataclass: Type):
    def parse(fn):
        def wrapper(*args, **kwargs):
            try:
                values = list(kwargs.values())
                if len(values) == 0:
                    return fn(*args)
                elif len(values) == 1:
                    if isinstance(values[0], dataclass):
                        return fn(*args, **kwargs)
                else:
                    input_fields = list(kwargs.keys())
                    dataclass_fields = [field.name for field in fields(dataclass)]
                    # if kwargs are a subset of dataclass fields we can try to instantiate the dataclass
                    if set(input_fields + dataclass_fields) == set(dataclass_fields):
                        inp = dataclass(**kwargs)
                        return fn(*args, inp)
            except TypeError as ex:
                raise ValueError(
                    f"Could not convert keyword arguments: {kwargs} to {dataclass.__name__}.\n{ex}"
                )

        return wrapper

    return parse


__version__ = "0.1.0"
