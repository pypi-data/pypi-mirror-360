from ..imports import *
from abstract_utilities import make_list
def get_all_case(objs):
    objs = make_list(objs or [])
    objs_copy = objs.copy()
    new_objs = []
    for i,obj in enumerate(objs):
        new_objs.append(obj)
        if isinstance(obj,str):
            new_objs.append(obj.lower())
            new_objs.append(obj.upper())
    return list(set(new_objs))
def is_true(obj):
    trues = get_all_case([True,'true','tru',1,float(1),'1'])
    if obj in trues:
        return True
    return False
def is_false(obj):
    falses = get_all_case([False,'false','fals',0,float(0),'0'])
    if obj in falses:
        return True
    return False
def toggle_var(obj):
    if is_true(obj):
        return False
    if is_false(obj):
        return True
    if obj:
        return False
    return True
def get_table_name(tableName,schema='public'):
    return sql.SQL('{}.{}').format(
        sql.Identifier(schema),
        sql.Identifier(tableName)
        )
def _build_set_clause(data_map):
    """
    Returns: (sql.SQL fragment, values list)
    """
    parts, vals = [], []
    for col, val in data_map.items():
        parts.append(sql.SQL("{} = %s").format(sql.Identifier(col)))
        vals.append(val)
    return sql.SQL(', ').join(parts), vals


def _build_where_clause(filter_map, values=None, *, any_value=False):
    """
    Returns: (sql.SQL fragment starting with ' WHERE …' or sql.SQL(''), values list)
    """
    if not filter_map:
        return sql.SQL(''), values or []

    parts, vals = [], values or []
    for col, val in filter_map.items():
        if any_value:
            parts.append(sql.SQL("{} = ANY(%s)").format(sql.Identifier(col)))
            vals.append(make_list(val))
        else:
            parts.append(sql.SQL("{} = %s").format(sql.Identifier(col)))
            vals.append(val)

    return sql.SQL(' WHERE ') + sql.SQL(' AND ').join(parts), vals

# ---------- SELECT -----------------------------------------------------------
def fetch_any_combo(*,
                    column_names='*',
                    table_name,
                    search_map=None,
                    count=False,
                    any_value=False,
                    zipit=True,
                    schema='public'):

    if not table_name or table_name == '*':
        logger.error("Invalid table_name provided to fetch_any_combo: %s", table_name)
        return []
    select_cols = None
    # SELECT list
    if count:
        select_cols = sql.SQL("COUNT(*)")
    elif column_names == '*':
        select_cols = sql.SQL('*')
    elif isinstance(column_names,str):
        column_names = [c.strip() for c in column_names.split(',')]
    if isinstance(column_names,list) and select_cols is None:
        select_cols = sql.SQL(', ').join(sql.Identifier(c) for c in column_names)

    base = sql.SQL("SELECT {} FROM {}.{}").format(
        select_cols,
        sql.Identifier(schema),
        sql.Identifier(table_name)
    )

    where_sql, params = _build_where_clause(search_map or {}, any_value=any_value)

    return query_data(base + where_sql, values=params, zipRows=zipit)


# ---------- UPDATE -----------------------------------------------------------
def update_any_combo(*,
                     table_name: str,
                     update_map: dict,
                     search_map: dict = None,
                     any_value: bool = False,
                     returning=False,        # False | True | 'count' | 'col1,col2'
                     zipit=True,
                     schema='public'):

    if not table_name or table_name == '*':
        raise ValueError("table_name is required")
    if not update_map:
        raise ValueError("update_map cannot be empty")

    set_sql, params = _build_set_clause(update_map)
    where_sql, params = _build_where_clause(search_map or {}, params, any_value=any_value)

    qry = (
        sql.SQL("UPDATE {}.{} SET ").format(sql.Identifier(schema),
                                            sql.Identifier(table_name))
        + set_sql
        + where_sql
    )

    if returning:
        if returning is True:
            qry += sql.SQL(' RETURNING *')
        elif returning == 'count':
            qry = sql.SQL("WITH upd AS (") + qry + sql.SQL(" RETURNING 1) SELECT COUNT(*) FROM upd")
        else:
            cols = [c.strip() for c in returning.split(',')]
            qry += sql.SQL(' RETURNING ') + sql.SQL(', ').join(sql.Identifier(c) for c in cols)

    return query_data(qry, values=params, zipRows=zipit)
def get_column_names(tableName,schema='public'):
    return columnNamesManager().get_column_names(tableName,schema)
def getZipRows(tableName, rows, schema='public'):
    columnNames = get_column_names(tableName,schema)
    if columnNames:
        return [dict(zip(columnNames,row)) for row in make_list(rows) if row]
def get_db_from(tableName=None,columnNames=None,searchColumn=None,searchValue=None,count=False,zipit=True):
    columnNames=columnNames or '*'
    if isinstance(columnNames,list):
        columnNames = ','.join(columnNames)
    response = fetch_any_combo(tableName=tableName,columnNames=columnNames,searchColumn=searchColumn,searchValue=searchValue,zipit=zipit,count=count)
    return response
def get_all_table_info(schema='public'):
    all_table_infos = {each:get_column_names(each) for each in get_all_table_names()}
    return all_table_infos
def get_value_from_row(row):
    if isinstance(row,list):
        for i,item in enumerate(row):
            if isinstance(item,dict):
                item = list(item.values())
            row[i] = item[0]
    if isinstance(row,dict):
        row = list(row.values())
        row = row[0]
    if isinstance(row,list) and len(row) == 1:
        row = row[0]
    return row
def fetch_combo_result(*arg,**kwargs):
    response = fetch_any_combo(*arg,**kwargs)
    result = get_value_from_row(response)
    return result
def toggle_result(*arg,**kwargs):
    responses = fetch_any_combo(*arg,**kwargs)
    kwargs['update_map']={}
    for response in responses:
        for key,value in response.items():
            kwargs['update_map'][key] = toggle_var(value)
    if 'column_names' in kwargs:
        del kwargs['column_names']
    result = update_any_combo(*arg,**kwargs)
    return result
