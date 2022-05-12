from inity import inity

@inity
class ExampleClass:
    a: int
    b: str

ec = ExampleClass(1, 2)
print(ec.a == 1)
# True
print(ec.b == 2)
# True
