# This version has been modified to work with 3.6 and above
# Dataclass related features are removed
# The convenience function "factory" is very limited. 
# Recommend making wrapper functions name {something}_factory instead

import re
import sys
import typing as t
from enum import Enum
from textwrap import dedent
from weakref import proxy

SNAKE_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
SNAKE_2 = re.compile(r"([a-z\d])([A-Z])")


class _MISSING_TYPE(str):
    pass


MISSING = _MISSING_TYPE("MISSING")


def upper_snake(string: str) -> str:
    return SNAKE_2.sub(
        r"\1_\2",
        SNAKE_1.sub(r"\1_\2", string),
    ).upper()


def _is_class_var(param_type) -> bool:
    if "ClassVar" in str(type(param_type)):
        # This is a hackey workaround for early
        # versions of typing not providing
        # __origin__
        return True
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
        else:
            raise TypeError(
                "Cannot make built-ins a factory in older versions of python."
                "\nMake a custom factory function instead."
            )
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
    property_shadow_prefix: t.ClassVar[str] = "_"

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

        default = getattr(mro, name, default)
        if name != MISSING and isinstance(default, Field):
            self.metadata.update(default.metadata)
            default = (
                default.default
                if default.default is not MISSING
                else factory(default.default_factory)
            )

        if callable(default) and self.factory_substring in default.__name__:
            default = default()

        self.default = default

    @property
    def field_type(self):
        if isinstance(self.default, property):
            return FieldType.PROPERTY_SHADOW
        elif FieldType.__members__.get(upper_snake(self.type_name)):
            return FieldType.__members__.get(upper_snake(self.type_name))
        else:
            return FieldType.STANDARD

    @property
    def has_default(self) -> bool:
        return False if self.default is MISSING else True

    @property
    def type_name(self):
        if _is_class_var(self.param_type):
            # Old versions of python do not have the __name__ attribute
            # on the types in typing.
            return "CLASS_VAR"
        return self.param_type.__name__

    @property
    def param(self):
        return f"{self.name}" + self.default_string(self.default)

    def default_string(self, default: t.Any) -> str:
        if isinstance(default, str):
            return f' = """{default}"""'
        elif isinstance(default, property):
            return " = None"
        if self.has_default:
            return f" = {getattr(default, '__name__', default)}"
        else:
            return ""

    @property
    def body_setter(self):
        if self.field_type.value >= 3:
            return ""
        prefix = (
            self.property_shadow_prefix
            if self.field_type == FieldType.PROPERTY_SHADOW
            else ""
        )
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

    def __init__(self, cls, field_class=Field, debug=False):
        self.cls = proxy(cls)
        self.field_class = field_class
        self.debug = debug
        self._fields = None

    @property
    def fields(self):
        if self._fields is None:
            self._fields = list(
                {
                    name: self.field_class(name=name, param_type=param_type, mro=mro)
                    for mro in self.cls.__mro__
                    for name, param_type in getattr(mro, "__annotations__", {}).items()
                }.values()
            )
        return self._fields

    def get_fields_of_type(self, field_type: FieldType) -> list:
        return [f for f in self.fields if f.field_type == field_type]

    @property
    def params(self):
        params = "self"
        no_default_fields = [
            f.param
            for f in self.fields
            if not _is_class_var(f.param_type) and not f.has_default
        ]
        if no_default_fields:
            params += ", " + ", ".join(no_default_fields)
        default_fields = [
            f.param
            for f in self.fields
            if not _is_class_var(f.param_type) and f.has_default
        ]
        if default_fields:
            params += ", *, " + ", ".join(default_fields)
        return params

    @property
    def body(self):
        body = "".join(f.body_setter for f in self.fields)
        if hasattr(self.cls, self.after_init_hook_name):
            initvars = self.get_fields_of_type(FieldType.INIT_VAR)
            if initvars:
                init_params = ", ".join([f"{iv.name} = {iv.name}" for iv in initvars])
            else:
                init_params = ""
            body += f"\n\tself.{self.after_init_hook_name}({init_params})"
        if not body:
            body = "\tpass"
        return body

    def exec_code(self, code):
        if self.debug is True:
            print(code)
        try:
            globals = sys.modules[self.cls.__module__].__dict__
            d = {}
            exec(code, globals, d)
            return d.popitem()[1]
        except (SyntaxError, NameError) as e:
            print(f"init failed in {self.cls}")
            print(code)
            raise e

    def build_init(self):
        return self.exec_code(
            self.INIT_TEMPLATE.format(params=self.params, body=self.body)
        )


def inity(*args, field_class=Field, initializer_class=Initializer, debug=False):
    if len(args) == 1 and callable(args[0]):
        return inity()(args[0])

    def init_builder(cls):
        if "__init__" not in vars(cls):
            initializer = initializer_class(cls, field_class=field_class, debug=debug)
            cls.__init__ = initializer.build_init()
            cls.fields = initializer.fields
        return cls

    return init_builder
