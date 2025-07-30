from .databaseManager import *
def ensure_db_manager(db_mgr=None, env_path=None, dbName=None, dbType=None, conn_mgr=None):
    return db_mgr or DatabaseManager(env_path=env_path, dbName=dbName, dbType=dbType, conn_mgr=conn_mgr)
