from ..imports import *
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
    protocol = 'postgresql'
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
