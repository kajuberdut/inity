<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** kajuberdut, inity, twitter_handle, patrick.shechet@gmail.com, inity, String functions in pure Python
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/kajuberdut/inity">
    <img src="https://raw.githubusercontent.com/kajuberdut/inity/main/images/icon.svg" alt="icon" width="160" height="160">
  </a>

  <h3 align="center">inity</h3>

  <p align="center">
    A small, easy __init__ generator.
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#usage">Usage</a>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <!-- <li><a href="#license">License</a></li> -->
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Inity provides a way to generate the __init__ method of python classes. Inity closely resembles attrs or dataclasses, only it's much smaller and less feature full than attrs and it handles default values in class inheritence in a more opinionated and easier to deal with way than dataclasses does.


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Installing with pip

  ```sh
  pip install inity
  ```

  Alternately, you can copy inity/core.py from this library into your own project and import from that.

For information about cloning and dev setup see: [Contributing](#Contributing)


<!-- USAGE EXAMPLES -->
## Usage

### Simple Case
Inity does not generate repr, or comparison methods like other similiar libraries. For the most part it only generates init.

```python
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

```

### VS Dataclasses
It's fairly anoying to combine dataclasses with the property decorator as seen (here)[https://florimond.dev/en/posts/2018/10/reconciling-dataclasses-and-properties-in-python/]

Inity takes an easy approach to this. If any field of your class shares a name with a property, the intial value will be stored in a _field_name field.

Example:
```python
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
```


Dataclasses also makes inheriting from classes with defaults painful as seen (here)[https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses]

Inity simply re-orders parameters so that the defaults are at the end of the set.

Example:
```python
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

```

### Other features
Inity will handle any callable ending in "_factory" that is set as a default. You can use the convenince function "factory" to update callables to meet his requirement.

Example:
```python
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

```

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Add tests, we aim for 100% test coverage [Using Coverage](https://coverage.readthedocs.io/en/coverage-5.3.1/#using-coverage-py)
4. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

### Cloning / Development setup
1. Clone the repo and install
    ```sh
    git clone https://github.com/kajuberdut/inity.git
    cd inity
    pipenv install --dev
    ```
2. Run tests
    ```sh
    pipenv shell
    ward
    ```
  For more about pipenv see: [Pipenv Github](https://github.com/pypa/pipenv)



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact

Patrick Shechet - patrick.shechet@gmail.com

Project Link: [https://github.com/kajuberdut/inity](https://github.com/kajuberdut/inity)




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/kajuberdut/inity.svg?style=for-the-badge
[contributors-url]: https://github.com/kajuberdut/inity/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/kajuberdut/inity.svg?style=for-the-badge
[forks-url]: https://github.com/kajuberdut/inity/network/members
[stars-shield]: https://img.shields.io/github/stars/kajuberdut/inity.svg?style=for-the-badge
[stars-url]: https://github.com/kajuberdut/inity/stargazers
[issues-shield]: https://img.shields.io/github/issues/kajuberdut/inity.svg?style=for-the-badge
[issues-url]: https://github.com/kajuberdut/inity/issues
[license-shield]: https://img.shields.io/badge/License-MIT-orange.svg?style=for-the-badge
[license-url]: https://github.com/kajuberdut/inity/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/patrick-shechet
