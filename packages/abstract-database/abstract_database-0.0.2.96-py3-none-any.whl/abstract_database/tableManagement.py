from abstract_utilities import safe_read_from_json,SingletonMeta,safe_dump_to_file
class TableManager(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config_mgr = configClass()
            self.initialized = True
            self.insert_list = []
            self.dbNames=[]
    def add_insert_list(self,conn,tables,dbName):
        if dbName not in self.dbNames:
            self.dbNames.append(dbName)
            setup_database(tables,conn)
            self.insert_list+=tables
    def get_insert(self, tableName):
        tableName = tableName.lower()
        insertList = [ls for ls in self.insert_list if ls.get("tableName") == tableName.lower()]
        return insertList[0] if insertList else None

    def fetchFromDb(self,tableName,searchValue,conn):
        cached_response = perform_database_operations('fetch', self.get_insert(tableName), searchValue, conn)
        if cached_response:
            return cached_response

    def insert_intoDb(self,tableName,searchValue,insertValue,conn):
        if isinstance(insertValue,dict):
            insertValue = json.dumps(insertValue)
        return perform_database_operations('insert', self.get_insert(tableName), (searchValue,insertValue),conn )
    def search_multiple_fields(self, query,conn,**kwargs):
        return search_multiple_fields(query,conn)
    def get_first_row_as_dict(self,tableName=None,rowNum=1,conn=None):
        """Fetch the first row of data from the specified table and return as a dictionary."""
        tableName = tableName or get_env_value(key="abstract_ai_table_name", path=self.env_path)
        query = f"SELECT * FROM {tableName} ORDER BY id ASC LIMIT {rowNum};"
        cur = conn.cursor()
        try:
            cur.execute(query)
            first_row = cur.fetchone()
            col_names = [desc[0] for desc in cur.description]
            if first_row:
                return dict(zip(col_names, first_row))
            return None
        except psycopg2.Error as e:
            print(f"Error fetching the first row: {e}")
            return None
        finally:
            cur.close()
            conn.close()
    def add_table_config(self,dbName,dbType):
        table_config = safe_read_from_json(get_table_path(dbName,dbType))
        self.table_configs+=table_config
    def add_unique_header(self,uniqueHeader,tableName,dbName,dbType):
        table_path = get_table_path(dbName,dbType)
        insertTables = safe_read_from_json(get_table_path(dbName,dbType))
        newTables = []
        tableName = tableName.lower()
        for i,insertTable in enumerate(insertTables):
            if tableName == insertTable.get('tableName'):
                if 'excelUniqueHeaders' not in insertTable:
                    insertTable['excelUniqueHeaders'] = []
                if uniqueHeader not in insertTable['excelUniqueHeaders']:
                    insertTable['excelUniqueHeaders'].append(uniqueHeader)
                    self.table_configs = [insertTable if table.get('tableName') == tableName else table for table in self.TableManager.table_configs]
            newTables.append(insertTable)
        safe_dump_to_file(data=newTables,file_path=table_path)

def add_unique_header(uniqueHeader,tableName,dbName,dbType):
    TableManager().add_unique_header(uniqueHeader,tableName,dbName,dbType)
def add_table_config(dbName,dbType):
    TableManager().add_table_config(dbName,dbType)
def get_table_path(dbName,dbType):
    key = f"{dbName.upper()}_{dbType.upper()}_CONFIGPATH"
    return get_env_value(path=get_env_path(),key=key)
