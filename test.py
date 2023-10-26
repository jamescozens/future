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

    def __str__(self):
        return f"MyClass instance with value: {self.name} and I am {self.age} years old"




person1 = Person("John", 30)
print(person1)

person1 = Person("Jim")
print(person1)