from inity import inity

@inity
class MyClass:
    name: str
    reversed: int = None

    @property
    def reversed(self):
        if self._reversed is None:
            print("generating reversed name")
            self._reversed = self.name[::-1]
        return self._reversed

 
instance = MyClass(name="inity")
print(instance.reversed)
# generating reversed name
# ytini

instance2 = MyClass(name="inity", reversed="I'm bad at reversing things")
print(instance2.reversed)
# I'm bad at reversing things