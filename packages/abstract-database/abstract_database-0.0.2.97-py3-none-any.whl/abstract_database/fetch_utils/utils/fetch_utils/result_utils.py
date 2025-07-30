from .fetch_utils import update_any_combo,get_value_from_row
from .utils import toggle_var,get_value_from_row
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
