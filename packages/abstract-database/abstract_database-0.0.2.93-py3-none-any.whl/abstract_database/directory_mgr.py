import os
def get_abs_path():
  return os.path.abspath(__name__)
def get_abs_dir():
  return os.path.dirname(get_abs_path())
def create_abs_path(path):
  return os.path.join(get_abs_dir(),path)
  
