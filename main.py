# main.py

# Import the module
# from jimpack import my_variable
import jimpack.one as x
import jimmod as j
import logging
import sqlite3


def function1():
    x = 1
    def function2() -> int:
        return inc()

    def inc() -> int:
        nonlocal x
        x += 2
        return x

    return function2

f = function1()
print(f())
print(f())
print(f())

logger = logging.getLogger(__name__)

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE IF NOT EXISTS A (A INT)")
res = con.execute("INSERT INTO A (A) VALUES ('DDDDD')")
con.commit()
res = con.execute("SELECT * FROM A")
print(res.fetchall())

con.close()


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
