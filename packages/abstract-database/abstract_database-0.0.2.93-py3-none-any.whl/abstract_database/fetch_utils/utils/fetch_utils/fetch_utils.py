from .utils import *
from ...imports import query_data
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

    where_sql, params = build_where_clause(search_map or {}, any_value=any_value)

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

    set_sql, params = build_set_clause(update_map)
    where_sql, params = build_where_clause(search_map or {}, params, any_value=any_value)

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
