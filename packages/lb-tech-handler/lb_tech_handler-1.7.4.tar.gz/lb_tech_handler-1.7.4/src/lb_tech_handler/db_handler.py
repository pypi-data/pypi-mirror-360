from encodings import ptcp154
import json
import os
import traceback
import warnings
from psycopg2 import pool
import psycopg2
import pandas as pd 
import multiprocessing
try:
    from lb_tech_handler.common_methods import timed_execution,timeit
except:
    from common_methods import timed_execution,timeit

from dotenv import load_dotenv

load_dotenv()

CPU_COUNT = os.cpu_count()

LB_DB_HOST_NAME_OR_IP = os.getenv(key='LB_DB_HOST_NAME_OR_IP',default='db.learnbasics.fun')

LB_DB_USER_NAME = os.getenv(key='LB_DB_USER_NAME')

LB_DB_PASSWORD = os.getenv(key='LB_DB_PASSWORD')

LB_DB_PORT = os.getenv(key='LB_DB_PORT',default=7777)

LB_DB_APPLICATION_NAME = os.getenv(key='LB_DB_APPLICATION_NAME',default='LB_DB_UNNAMED_APPLICATION')

LB_DB_DATABASE_NAME = os.getenv(key='LB_DB_DATABASE_NAME',default='lb_db')

LB_DB_MIN_CONN = os.getenv(key='LB_DB_MIN_CONN',default=1)

LB_DB_MAX_CONN = os.getenv(key='LB_DB_MAX_CONN',default=CPU_COUNT)

LB_DB_LOG_FILE_PATH = os.getenv(key='LB_DB_LOG_FILE_PATH',default='db.log') 

db_pool = pool.SimpleConnectionPool(
    minconn = LB_DB_MIN_CONN,
    maxconn = LB_DB_MAX_CONN * 2,
    database = LB_DB_DATABASE_NAME,
    user = LB_DB_USER_NAME,
    password = LB_DB_PASSWORD,
    host = LB_DB_HOST_NAME_OR_IP,
    port = LB_DB_PORT,
    application_name = LB_DB_APPLICATION_NAME
)

def get_dataframe_from_query(query: str,vars={},return_json=False) -> pd.DataFrame:

    """_summary_

    Args:
        query (str): _description_
        vars (dict, optional): _description_. Defaults to {}.

    Returns:
        _type_: _description_
    """


    try:
        conn:psycopg2.extensions.connection = db_pool.getconn()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            table = pd.read_sql(query, con=conn, params=vars)

        db_pool.putconn(conn)

        if return_json:

            json_df = json.loads(table.to_json(orient='records'))

            return json_df
        
        return table
        
    except Exception as e:
        db_pool.putconn(conn=conn,close=True)
        raise Exception(e)


    

def get_dataframe_from_list_of_queries(list_of_queries:list[dict]) -> list[pd.DataFrame]:
    """returns the query as pandas dataframe from database

    Input Format:
        [
            {
                'query':query,
                'vars':{
                    "key1":"value1",
                    "key2":"value2"
                }
            },
            {
                'query':query2,
                'vars':{
                    "key1":"value1",
                    "key2":"value2"
                }
            }
        ]

    Args:
    --------
        query (str): query
    
    Returns:
    ---------
        data: pandas dataframe from query
    """

    try:
        with multiprocessing.Pool(processes=CPU_COUNT) as pool:
            results = pool.starmap(get_dataframe_from_query,[(sub_queries['query'],sub_queries['vars'] ) for sub_queries in list_of_queries])

    except Exception as e:
        raise Exception(e)

  
    return results



def execute_query(query:str,vars={}):
    """_summary_

    Args:
        query (str): _description_
        vars (dict, optional): _description_. Defaults to {}.

    Raises:
        Exception: _description_
    """

    try:
        conn:psycopg2.extensions.connection = db_pool.getconn()

        cursor = conn.cursor()   
        cursor.execute(query=query,vars=vars)
        conn.commit()
        
        db_pool.putconn(conn=conn)
    except Exception as e:

        conn.rollback()

        db_pool.putconn(conn=conn,close=True)
        raise Exception(e)


def execute_query_and_return_result(query:str,vars={},fetchall=True) -> list:
    """_summary_

    Args:
        query (str): _description_
        vars (dict, optional): _description_. Defaults to {}.

    Raises:
        Exception: _description_

    Returns:
        list: _description_
    """
    try:

        conn:psycopg2.extensions.connection = db_pool.getconn()
        
        cursor = conn.cursor()   

        cursor.execute(query=query,vars=vars)

        conn.commit()

        data =  cursor.fetchall()

        db_pool.putconn(conn=conn)

        if fetchall:
            return data
        else:
            if len(data) > 0:
                return data[0]
            else:
                return None
    except Exception as e:

        conn.rollback() 

        db_pool.putconn(conn=conn,close=True)

        raise Exception(e)

def execute_transaction(list_of_queries:list[dict]):

    """Executes a list of queries

    Input Format:
        
        [
            {
                'query':query,
                'vars':{
                    "key1":"value1",
                    "key2":"value2"
                }
            },
            {
                'query':query2,
                'vars':{
                    "key1":"value1",
                    "key2":"value4"
                }
            }
        ]
        

    Args:
    --------
        query (str): query
        vars (dict, optional): _description_. Defaults to {}.
    
    Returns:
    ---------
        is_transaction_successful: bool
    """


    try:
        conn:psycopg2.extensions.connection = db_pool.getconn()

        cursor = conn.cursor()

        for query in list_of_queries:
            cursor.execute(query=query['query'],vars=query['vars'])
        
        conn.commit()
        
        
        db_pool.putconn(conn=conn)

        return True

    except Exception as e:
        conn.rollback()

        db_pool.putconn(conn=conn,close=True)  
        
        raise Exception(e)

def execute_transaction_with_multiprocessing(list_of_queries:list[dict],MAX_PROCESS:int=CPU_COUNT) -> bool:
    """This is a function to execute a list of queries in parallel using multiprocessing
    Use this when you have a list of queries and want to execute them in parallel 

    Args:

    - list_of_queries (list[dict]): 
    
    Input Format:

            [
                {
                    'query':query,
                    'vars':{
                        "key1":"value1",
                        "key2":"value2"
                    }
                },
                {
                    'query':query2,
                    'vars':{
                        "key1":"value1",
                        "key2":"value2"
                    }
                }
            ]

    - MAX_PROCESS (int, optional): Maximum number of processes to use. 
        - Defaults to CPU_COUNT.

    Returns:
        bool: _description_
    """
    sub_queries_list = []

    for i in range(0,len(list_of_queries),MAX_PROCESS):
        sub_queries_list.append(list_of_queries[i:i+MAX_PROCESS])

    with multiprocessing.Pool(processes=MAX_PROCESS) as pool:
        pool.starmap(execute_transaction,[(sub_queries, ) for sub_queries in sub_queries_list])

    return True

    
def get_connection_from_pool():
    return db_pool.getconn()

def put_connection_in_pool(conn):
    db_pool.putconn(conn=conn)

def is_free_connection_in_pool() -> bool:

    return LB_DB_MAX_CONN - len(db_pool._used) > 0

def test_excution_multi_query(list_of_queries:list[dict]):
    for query in list_of_queries:
        execute_query(query=query['query'],vars=query['vars'])

@timed_execution
def test_async_query():
    execute_query("insert into public.test (name) values ('Testing Data')")



if __name__ == "__main__":

    df = get_dataframe_from_query(
        query="select * from public.test",
        return_json=True
    )

    print(df)
    
    print(type(df))
    # for i in range(0,100):
    #     test_async_query()