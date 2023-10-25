# main.py

# Import the module
# from jimpack import my_variable
import jimpack.one as x
import jimmod as j



def main():
    print("Hello World!")

    # Access the variable and call the function
    print(x.my_variable)
    result = x.greet("Alice")
    print(result)

    # Access the variable and call the function
    print(j.my_variable)
    result = j.greet("Alice")
    print(result)


if __name__ == "__main__":
    main()


