print("Hello, World!")


if 2>3:
    print(repr(True))
else:
    print(repr(False))

class Person:
    name = None
    age = None

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __init__(self, *args):
        if len(args) == 0:
            print("No arguments provided")
        elif len(args) == 1:
            self.name = args[0]
#            self.age = None
        else:
            self.name = args[0]
            self.age = args[1]

    def __add__(self, other):
        if isinstance(other, Person):
            return Person(  ("" if self.name is None else self.name) + " " + ("" if other.name is None else other.name), \
                            ( None if (self.age is None or other.age is None) else self.age + other.age) )
        else:
            # If 'other' is not a Person object, raise an exception
            raise TypeError("You can only add Person objects together")


    def __str__(self):
        return f"MyClass instance with value: {self.name} and I am {self.age} years old"




person1 = Person("John", 30)
print(person1)

person2 = Person("Jim")
print(person1)

print(person1 + person2)
