# from database import connect, insertDF, create_tableimp
import psycopg2
from psycopg2 import Error
import psycopg2.extras as extras
import numpy as np
import pandas as pd


def connect(): 
    # establish a connection to postgreSQL
    try: 
        connection = psycopg2.connect(
            user = "postgres",
            password = "your_pw", # insert your own password
            host = "localhost",
            port = "5432",
            database = "hktvmall"
        )
        cursor = connection.cursor()
        print('Server information', connection.get_dsn_parameters(), '\n')
        # optional printout
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print('Connected to ', record, '\n')

        return connection

    except {Exception, Error} as error:
        print("Error connecting to postgreSQL", error)
        return False

if __name__ == '__main__':
    print('running main')
    connect()

def create_table():
    command = (
    """
    CREATE TABLE parenting_product (
        website VARCHAR(255) NOT NULL,
        product_cate VARCHAR(255) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        package VARCHAR(255),
        sales FLOAT,
        rating FLOAT,
        review_number FLOAT,
        original_price FLOAT,
        selling_price FLOAT,
        vendor_name VARCHAR(255) NOT NULL,
        origin VARCHAR(255),
        star5_comment VARCHAR(10000),
        star1_comment VARCHAR(10000),
        date DATE NOT NULL
    )
    """
    )
    try: 
        connection = connect()
        if connection:
            cursor = connection.cursor() # create a tool to manipulate the sql
            resp = cursor.execute(command) # execute the saved sql command
            cursor.close() # must close
            connection.commit() # deliever the change, without it, sql may not be change, like a confirmation
            print('Created table in postgreSQL')
        else:
            print('connection invalid')

    except (Exception, Error) as error:
        print("Error connecting to postgreSQL", error)
        return False

    finally: # no matter success or not, finally must be run
        if connection is not None:
                connection.close()

if __name__ == '__main__':
    print('running main')
    # connect() 
    create_table()
    # first run: connect the sever
        # connect enable, create_table disable
    # second run: create table 
        # connect disable, create_table enable
    
    
def insertDF(connection, df, table):
    tuple_list = [tuple(x) for x in df.to_numpy()]

    print ('Tuple')
    # for _tuple in tuple_list:
        # print(_tuple)

    cols = ','.join(list(df.columns)) # put df title into a str separeted with
    # print('Cols')
    # print(cols)


    # option (1/3)
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols) # a command can be execuated in sql # can use f string to do so
    # option (2/3)
        # method 1 to aviod repeating
    # query = "INSERT INTO %s(%s) VALUES %%s ON CONFLICT (product_name, vendor_name, date) DO NOTHING;" % (table, cols)
    # option (3/3)
        # method 2 to aviod repeating
    # query = "INSERT INTO %s(%s) VALUES %%s ON CONFLICT (product_name, vendor_name, date) DO UPDATE SET (date) = ROW(EXCLUDED.date);" % (table, cols)
    
    # print(f'\n\nQuery:{query}')

    cursor = connection.cursor()
    try:
        extras.execute_values(cursor, query, tuple_list) # insert the value multiple times
        connection.commit() # deliever the change

    except (Exception, Error) as error:
        print("Error connecting to postgreSQL", error)
        return False
    
    finally: 
        cursor.close()
        return True

# how to recall the data in sql again
def sql_to_df(connection, table):
    df = pd.read_sql("SELECT * FROM %s;" % (table), connection)
                            # %S = table name, which is air_force_one
    # print(df)
    return df


if __name__ == '__main__':
    print('running main')
    # connect()
    # create_table()
