from inity import factory, inity

def some_factory():
    return 314

df = factory(dict)

@inity
class FactoryLane:
    a: int = some_factory
    b: dict = df
    c: str = factory(lambda: "hi")
    d: int = factory(int)
    not_a_factory = str

fl = FactoryLane()
print(fl.a)
# 314
print(fl.b)
# {}
print(fl.c)
# hi
print(fl.d)
# 0
print(fl.not_a_factory)
# <class 'str'>
