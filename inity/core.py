import re
import sys
import typing as t
from dataclasses import MISSING
from dataclasses import Field as _Field
from enum import Enum
from functools import cached_property, singledispatchmethod
from textwrap import dedent
from weakref import proxy

SNAKE_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
SNAKE_2 = re.compile(r"([a-z\d])([A-Z])")


def upper_snake(string: str) -> str:
    return SNAKE_2.sub(
        r"\1_\2",
        SNAKE_1.sub(r"\1_\2", string),
    ).upper()


def _is_class_var(param_type) -> bool:
    if hasattr(param_type, "__origin__"):
        param_type = param_type.__origin__
    if param_type is t.ClassVar:
        return True
    else:
        return False


def factory(callable: t.Callable) -> t.Callable:
    _factory = callable
    try:
        _factory.__name__ = callable.__name__ + "_factory"
    except TypeError as e:
        if "of immutable type " in str(e):
            return factory(lambda: callable())
    return _factory


def as_dict(cls):
    return {f.name: getattr(cls, f.name) for f in cls.fields}


class InitVar:
    ...


FieldType = Enum("FieldType", "STANDARD PROPERTY_SHADOW INIT_VAR CLASS_VAR")


class Field:
    default: t.Any
    field_type: FieldType

    factory_substring: t.ClassVar[str] = "_factory"

    def __init__(
        self,
        name: str = MISSING,
        param_type: type = MISSING,
        default=MISSING,
        mro: type = None,
        metadata=None,
    ):
        self.name = name
        self.param_type = param_type
        self.metadata = {} if metadata is None else metadata

        if name != MISSING and isinstance(
            default := getattr(mro, name, default), (Field, _Field)
        ):
            self.metadata.update(default.metadata)
            default = (
                default.default
                if default.default is not MISSING
                else factory(default.default_factory)
            )

        if callable(default) and self.factory_substring in default.__name__:
            default = default()

        self.default = default

    @cached_property
    def field_type(self):
        if isinstance(self.default, property):
            return FieldType.PROPERTY_SHADOW
        elif ft := FieldType.__members__.get(upper_snake(self.type_name)):
            return ft
        else:
            return FieldType.STANDARD

    @property
    def has_default(self) -> bool:
        return False if self.default is MISSING else True

    @property
    def type_name(self):
        return self.param_type.__name__

    @property
    def param(self):
        return f"{self.name}" + self.default_string(self.default)

    @singledispatchmethod
    def default_string(self, default: t.Any) -> str:
        if self.has_default:
            return f" = {getattr(default, '__name__', default)}"
        else:
            return ""

    @default_string.register
    def _(self, default: str) -> str:
        return f' = """{default}"""'

    @default_string.register
    def _(self, default: property) -> str:
        return " = None"

    @property
    def body_setter(self):
        if self.field_type.value >= 3:
            return ""
        prefix = "_" if self.field_type == FieldType.PROPERTY_SHADOW else ""
        name = self.name
        return f"\n\tself.{prefix}{name} = {name}"


class Initializer:

    after_init_hook_name: t.ClassVar[str] = "after_init"
    INIT_TEMPLATE: str = dedent(
        """
        def __init__({params}) -> None:
        {body}
        """
    )

    def __init__(self, cls, field_class=Field):
        self.cls = proxy(cls)
        self.field_class = field_class

    @cached_property
    def fields(self):
        return list(
            {
                name: self.field_class(name=name, param_type=param_type, mro=mro)
                for mro in self.cls.__mro__
                for name, param_type in getattr(mro, "__annotations__", {}).items()
            }.values()
        )

    def get_fields_of_type(self, field_type: FieldType) -> list[Field]:
        return [f for f in self.fields if f.field_type == field_type]

    @property
    def params(self):
        params = "self"
        if no_default_fields := [
            f.param
            for f in self.fields
            if not _is_class_var(f.param_type) and not f.has_default
        ]:
            params += ", " + ", ".join(no_default_fields)
        if default_fields := [
            f.param
            for f in self.fields
            if not _is_class_var(f.param_type) and f.has_default
        ]:
            params += ", *, " + ", ".join(default_fields)
        return params

    @property
    def body(self):
        body = "".join(f.body_setter for f in self.fields)
        if hasattr(self.cls, self.after_init_hook_name):
            if initvars := self.get_fields_of_type(FieldType.INIT_VAR):
                init_params = ", ".join([f"{iv.name} = {iv.name}" for iv in initvars])
            else:
                init_params = ""
            body += f"\n\tself.{self.after_init_hook_name}({init_params})"
        if not body:
            body = "\tpass"
        return body

    def exec_code(self, code):
        try:
            globals = sys.modules[self.cls.__module__].__dict__
            exec(code, globals, d := {})
            return d.popitem()[1]
        except (SyntaxError, NameError) as e:
            print(f"init failed in {self.cls}")
            print(code)
            raise e

    def build_init(self):
        return self.exec_code(
            self.INIT_TEMPLATE.format(params=self.params, body=self.body)
        )


def inity(*args, field_class=Field, initializer_class=Initializer):
    if len(args) == 1 and callable(args[0]):
        return inity()(args[0])

    def init_builder(cls):
        if "__init__" not in vars(cls):
            initializer = initializer_class(cls, field_class=field_class)
            cls.__init__ = initializer.build_init()
            cls.fields = initializer.fields
        return cls

    return init_builder
