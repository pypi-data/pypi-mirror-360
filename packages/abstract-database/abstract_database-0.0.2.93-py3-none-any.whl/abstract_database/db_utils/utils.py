from abstract_utilities import safe_read_from_json
import json,inspect,hashlib,os
def make_single(string):
  return string.replace('_','')
def make_multiple(string):
    nustring=''
    uppers = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    for char in string:
        if char in uppers:
            char = f"_{char.lower()}"
        nustring+=char
    return nustring
def generate_data_hash(insertName,value):
    # Combine values to create a unique reference
    data_string = f"{insertName}_{value}"
    return hashlib.md5(data_string.encode()).hexdigest()
def isany_instance(value):
    for each in [dict, list, int, float]:
        if isinstance(value, each):
            return True
