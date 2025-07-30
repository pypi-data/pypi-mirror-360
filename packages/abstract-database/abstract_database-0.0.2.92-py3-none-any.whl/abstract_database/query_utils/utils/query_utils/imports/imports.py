from abstract_utilities import make_list,SingletonMeta,get_logFile
import psycopg2
from psycopg2.extras import RealDictCursor
from abstract_flask import initialize_call_log
from abstract_utilities import make_list,SingletonMeta
from psycopg2 import sql, connect
from abstract_security import get_env_value
import traceback
import warnings
from .....managers.connectionManager.utils import connect_db
logger = get_logFile('fetch_utils')
