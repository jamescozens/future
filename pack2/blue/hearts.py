from psycopg2 import connect
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from util.logger import logMe, getLogger

class DataException(Exception):
    """Still an exception raised when uncommon things happen"""

    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload  # you could add more args

    def __str__(self):
        return str(
            self.message)  # __str__() obviously expects a string to be returned, so make sure not to send any other data types

conn = None

try:
    conn = connect(
        host="localhost",
        database="future",
        user="postgres",
        password="password")
except DataException as e:
    print("DataException - connect - : Something went wrong", e)
except Exception as e:
    print("Exception - connect - Something went wrong", e)
finally:
    if conn is not None and not conn.closed:
        print("closing single connection...")
        conn.close()
    print("finally - signal connection - the 'try except' is finished")


#connection_pool: SimpleConnectionPool = None
connection_pool= None

try:
    # pool define with 10 live connections
    connection_pool = SimpleConnectionPool(1, 10, host="localhost",
                                           database="future",
                                           user="postgres",
                                           password="password",
                                           options="-c search_path=dev1,public")
    @logMe()
    @contextmanager
    def getCursor():
        con = connection_pool.getconn()
        try:
            yield con.cursor()
        finally:
            connection_pool.putconn(con)

    @logMe()
    def main_work():
        try:
            # with here will take care of put connection when its done
            with getCursor() as cur:
                cur.execute("select * from test1")
                result_set = cur.fetchall()
                for row in result_set:
                    getLogger(__name__).debug('---- '+str(row))
        except Exception as e:
            print("SQL: error in executing with exception: ", e)


    main_work()

except DataException as e:
    print("Connection Pool - DataException : Connection Pool - Something went wrong" , e)
except Exception as e:
    print("Connection Pool - Exception - Something went wrong" , e)
finally:
    if connection_pool is not None and not connection_pool.closed:
        print("closing connection pool...")
        conn.close()
    print("Finally: for connection pool is finished")

