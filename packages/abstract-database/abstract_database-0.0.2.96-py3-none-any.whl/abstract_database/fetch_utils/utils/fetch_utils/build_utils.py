from ...imports import sql
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
