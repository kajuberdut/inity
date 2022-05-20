import typing as t
from dataclasses import field
from unittest import TestCase, main

from inity import Field, InitVar, factory, inity, as_dict
from inity.core import Initializer


class TestInity(TestCase):
    def test_basic_init(self):
        @inity
        class Bob:
            some_int: int
            some_str: str

        b = Bob(some_int=1, some_str="s")
        self.assertEqual(b.some_int, 1)
        self.assertEqual(b.some_str, "s")

    def test_property_shadow(self):
        @inity
        class Jim:
            will_shadow: int

            @property
            def will_shadow(self):
                return self._will_shadow

        j = Jim(will_shadow=10)

        self.assertEqual(j.will_shadow, 10)
        self.assertEqual(j._will_shadow, 10)

    def test_default_factory(self):
        def some_factory():
            return 314

        df = factory(dict)

        @inity
        class FactoryLane:
            a: int = some_factory
            b: dict = df
            c: str = factory(lambda: "hi")
            d: int = factory(int)

        fl = FactoryLane()
        self.assertEqual(fl.a, 314)
        self.assertEqual(fl.b, {})
        self.assertEqual(fl.c, "hi")
        self.assertEqual(fl.d, 0)

    def test_dataclass_field(self):
        @inity
        class Something:
            has_default: int = field(default=1, metadata={"hello": "world"})
            also_has_default: dict = field(default_factory=dict)

        s = Something()
        self.assertEqual(s.has_default, 1)
        df = next((f for f in s.fields if f.name == "has_default"))
        self.assertEqual(df.metadata["hello"], "world")
        self.assertEqual(s.also_has_default, {})

    def test_inity_field(self):
        @inity
        class SomethingElse:
            has_default: int = Field(default=1, metadata={"hello": "world"})
            also_has_default: dict = Field(default=factory(dict))

        se = SomethingElse()
        self.assertEqual(se.has_default, 1)
        df = next((f for f in se.fields if f.name == "has_default"))
        self.assertEqual(df.metadata["hello"], "world")
        self.assertEqual(se.also_has_default, {})

    def test_class_var(self):
        @inity
        class Classy:
            class_var: t.ClassVar[str] = "Don't init me"

        self.assertRaises(TypeError, Classy, class_var="fail!")
        c = Classy()
        self.assertEqual(c.class_var, "Don't init me")

    def test_post_init(self):
        @inity
        class Posty:
            init_var: InitVar

            def after_init(self, init_var):
                self.holder = init_var

        p = Posty(init_var="something")
        self.assertEqual(p.holder, "something")

    def test_inheritance(self):
        @inity
        class FirstClass:
            has_default: int = 1
            shadowed_class_var: t.ClassVar[str] = "class version"

        @inity
        class SecondClass(FirstClass):
            class_var: t.ClassVar[str] = "Don't init me"
            no_default: str
            also_has_default: int = 2
            shadowed_class_var: str = "instance version"

        sc = SecondClass(no_default="ahhhhh!")
        self.assertEqual(sc.has_default, 1)
        self.assertEqual(sc.no_default, "ahhhhh!")
        self.assertEqual(sc.also_has_default, 2)
        self.assertEqual(sc.shadowed_class_var, "instance version")
        self.assertEqual(FirstClass.shadowed_class_var, "class version")

    def test_custom_class(self):
        class CustomField(Field):
            factory_substring = "__x__"
            property_shadow_prefix = "prop_"

        class CustomInit(Initializer):
            after_init_hook_name = "bob"

        def cacoon__x__():
            return "butterfly"

        @inity(field_class=CustomField, initializer_class=CustomInit, debug=True)
        class VeryCustom:
            thing: int = cacoon__x__
            shadow: int

            def bob(self):
                self.after_init = "hi"
                
            @property
            def shadow(self):
                return self.prop_shadow

        vc = VeryCustom(shadow = 1)
        self.assertEqual(vc.thing, "butterfly")
        self.assertEqual(vc.after_init, "hi")
        self.assertIsInstance(vc.fields[0], CustomField)
        self.assertEqual(vc.shadow, 1)

    def test_as_dict(self):
        @inity
        class BeADict:
            a: int = 1
            b: int = 2
            c: str = "hi"

        self.assertEqual(as_dict(BeADict()), {"a": 1, "b": 2, "c": "hi"})


if __name__ == "__main__":
    main()  # pragma: no cover
