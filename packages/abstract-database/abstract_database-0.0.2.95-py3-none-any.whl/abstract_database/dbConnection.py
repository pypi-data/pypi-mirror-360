from dbSearchFunctions import *

from psycopg2 import pool
import psycopg2
# Initialize the connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, user='catalyst',
                                                      password='catalyst',
                                                      host='192.168.0.100',
                                                      port='5432',
                                                      database='catalyst')

def get_db_connection():
    return connection_pool.getconn()
def put_db_connection(conn):
    connection_pool.putconn(conn)
def connect_db():
    """ Establish a connection to the database """
    return psycopg2.connect(
        dbname="catalyst",
        user="catalyst",
        password="catalyst",
        host="192.168.0.100",
        port=5432
    )
def makeRpcCall(method='',params=None,jsonrpc=None,id=None,headers=None,get_post="POST",endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    """
    Makes an RPC call using the provided method and parameters.
    """
    # Check if the response already exists in the database

    cached_response = fetchFromDb(method,params[0],get_db_connection())
    if cached_response:
        return cached_response
    # If no cached response exists, proceed with the RPC call
    response = rpc_call(method=method,params=params,jsonrpc=jsonrpc,id=id,headers=headers,get_post=get_post,endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
    # Save the response to the database for future use
    # Save the response to the database for future use
    insert_intoDb(method,params[0],response,connect_db())
    return response
def rpc_call(method='',params=None,jsonrpc=None,id=None,headers=None,get_post="POST",endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    """
    Makes an RPC call using the provided method and parameters.
    """
    # If no cached response exists, proceed with the RPC call
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    url = get_rate_limit_url(method).get('url')
    response = make_request(url, data, headers=headers, endpoint=endpoint,get_post=get_post, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
    log_response(method,response)
    # Save the response to the database for future use
##    return response
def is_in_db_list(method):
    if method.lower() in "gettransaction,getblock,".split(','):
        return makeRpcDbCall
    return rpc_call
"4LqCrcBSe2gn1wy5MkGu5yycDyHAUgCGPfwqs95FgJczg6odB9b9gSxbeaicg9KV8bXENiuvrYyhD2YcCxFMgQij"
