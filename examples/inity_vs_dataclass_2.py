from inity import inity

@inity
class FirstClass:
    has_default: int = 1

@inity
class SecondClass(FirstClass):
    no_default: str
    
instance = SecondClass("hi")

print(instance.has_default)
# 1
print(instance.no_default)
# hi
