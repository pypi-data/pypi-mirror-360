import psycopg2
from psycopg2 import pool
from abstract_utilities import is_number, SingletonMeta, safe_read_from_json
from abstract_security import *
from abstract_utilities import safe_read_from_json
from abstract_database.dbSearchFunctions import *
from urllib.parse import quote_plus


def get_safe_password(password):
    safe_password = quote_plus(password)
    return safe_password
# Existing utility functions remain the same
def get_dbType(dbType=None):
    return dbType or 'database'

def get_dbName(dbName=None):
    return dbName or 'abstract'

def verify_env_path(env_path=None):
    return env_path or get_env_path()

def get_db_env_key(dbType=None, dbName=None, key=None):
    dbType = get_dbType(dbType=dbType)
    dbName = get_dbName(dbName=dbName)
    return f"{dbName.upper()}_{dbType.upper()}_{key.upper()}"

def get_env_key_value(dbType=None, dbName=None, key=None, env_path=None):
    dbType = get_dbType(dbType=dbType)
    dbName = get_dbName(dbName=dbName)
    env_path = verify_env_path(env_path=env_path)
    env_key = get_db_env_key(dbType=dbType, dbName=dbName, key=key)
    return get_env_value(key=env_key, path=env_path)

def get_db_vars(env_path=None, dbType=None, dbName=None):
    dbVars = {}
    protocol = 'postgres'
    if 'rabbit' in dbType.lower():
        protocol = 'amqp'
    for key in ['user', 'password', 'host', 'port', 'dbname']:
        value = get_env_key_value(dbType=dbType, dbName=dbName, key=key, env_path=env_path)
        
        if is_number(value):
            value = int(value)
   
        dbVars[key] = value
    dbVars['dburl'] = f"{protocol}://{dbVars['user']}:{dbVars['password']}@{dbVars['host']}:{dbVars['port']}/{dbVars['dbname']}"
    return dbVars

def safe_load_from_json(file_path=None):
    if file_path:
        return safe_load_from_json(file_path)

class connectionManager(metaclass=SingletonMeta):
        
    def __init__(self, env_path=None, dbType=None, dbName=None, tables=[], tables_path=None,dbVars=None):
        if not hasattr(self, 'initialized'):
            self.initialized=True
            self.env_path = self.get_env_path(env_path=env_path)
            
            self.dbName = get_dbName(dbName=dbName)
            
            self.dbType = get_dbType(dbType=dbType)
            
            self.dbVars = dbVars or self.get_db_vars(dbType=self.dbType, dbName=self.dbName, env_path=self.env_path)
            self.user = self.dbVars['user']
            self.password = self.dbVars['password']
            self.host = self.dbVars['host']
            self.port = self.dbVars['port']
            self.dbname = self.dbVars['dbname']
            self.dburl = self.dbVars['dburl']  # URL-based connection string
            self.table_mgr = TableManager()
            self.tables = tables or safe_load_from_json(file_path=tables_path) or []
            self.table_mgr.env_path = self.env_path
            self.add_insert_list=None
            
            self.check_conn()
        
    def check_conn(self):
        if self.add_insert_list == None:
          try:
                self.table_mgr.add_insert_list(self.connect_db(), self.tables, self.dbName)
                self.table_mgr.add_insert_list(self.connect_db(), self.tables, self.dbName)
                self.add_insert_list=True
          except:
            pass
        return self.add_insert_list
    def get_dbName(self, dbName=None):
        return get_dbName(dbName=dbName or self.dbName)
    def get_dbType(self, dbType=None):
        return get_dbType(dbType=dbType or self.dbType)
    def get_env_path(self, env_path=None):
        return verify_env_path(env_path=env_path)

    def get_db_vars(self, env_path=None, dbType=None, dbName=None):
        env_path = self.get_env_path(env_path=env_path)
        dbName = self.get_dbName(dbName=dbName)
        dbType = self.get_dbType(dbType=dbType)
        dbVars = get_db_vars(env_path=env_path, dbType=dbType, dbName=dbName)
        return dbVars

    def change_db_vars(self, env_path=None, dbType=None, dbName=None, tables=[]):
        self.env_path = self.get_env_path(env_path=env_path)
        self.dbName = self.get_dbName(dbName=dbName)
        
        self.dbType = self.get_dbType(dbType=dbType)
        self.dbVars = self.get_db_vars(env_path=self.env_path, dbType=dbType, dbName=dbName)
        self.user = self.dbVars['user']
        self.password = self.dbVars['password']
        self.host = self.dbVars['host']
        self.port = self.dbVars['port']
        self.dbname = self.dbVars['dbname']
        self.dburl = self.dbVars['dburl']
        self.simple_connect = self.simple_connect_db()
        self.get_db_connection(self.connect_db())
        self.tables = tables or self.tables
        self.table_mgr.add_insert_list(self.connect_db(), self.tables, self.dbName)
        return self.dbVars

    def connect_db(self):
            
            """ Establish a connection to the database, either by connection parameters or via URL """
            if self.dburl:
                
                return psycopg2.connect(self.dburl)
            else:
                return psycopg2.connect(user=self.user,
                                        password=self.password,
                                        host=self.host,
                                        port=self.port,
                                        dbname=self.dbname)

    def simple_connect_db(self):
        """ Create a connection pool using the database URL """
        if self.dburl:
            return psycopg2.pool.SimpleConnectionPool(1, 10, self.dburl)
        else:
            return psycopg2.pool.SimpleConnectionPool(1, 10, user=self.user,
                                                      password=self.password,
                                                      host=self.host,
                                                      port=self.port,
                                                      database=self.dbname)

    def put_db_connection(self, conn):
        conn = conn or self.connect_db()
        self.putconn(conn)

    def get_db_connection(self):
        return self.connect_db()

    def get_insert(self, tableName):
        return self.table_mgr.get_insert(tableName)

    def fetchFromDb(self, tableName, searchValue):
        return self.table_mgr.fetchFromDb(tableName, searchValue, self.connect_db())

    def insertIntoDb(self, tableName, searchValue, insertValue):
        return self.table_mgr.insert_intoDb(tableName, searchValue, insertValue, self.connect_db())

    def search_multiple_fields(self, query, **kwargs):
        return self.table_mgr.search_multiple_fields(query=query, conn=self.connect_db())

    def get_first_row_as_dict(self, tableName=None, rowNum=1):
        return self.table_mgr.get_first_row_as_dict(tableName=tableName, rowNum=rowNum, conn=self.connect_db())

# Functions to interact with the connection manager
def create_connection(env_path=None, dbType=None, dbName=None):
    return connectionManager(env_path=env_path, dbType=dbType, dbName=dbName)

def get_db_connection():
    return connectionManager().get_db_connection()

def put_db_connection(conn):
    connectionManager().put_db_connection(conn)

def connect_db():
    return connectionManager().connect_db()

def get_insert(tableName):
    return connectionManager().get_insert(tableName)

def fetchFromDb(tableName, searchValue):
    return connectionManager().fetchFromDb(tableName, searchValue)

def insertIntoDb(tableName, searchValue, insertValue):
    return connectionManager().insertIntoDb(tableName, searchValue, insertValue)

def search_multiple_fields(query, **kwargs):
    return connectionManager().search_multiple_fields(query, **kwargs)

def get_first_row_as_dict(tableName=None, rowNum=1):
    return connectionManager().get_first_row_as_dict(tableName, rowNum)
