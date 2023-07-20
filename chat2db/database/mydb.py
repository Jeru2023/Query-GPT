import pandas as pd
from sqlalchemy import create_engine
import configparser as cp

class MyDB:
    def __init__(self, config_path='../config/sphinx.config'):
        self.config_path = config_path
        
        self.config = cp.ConfigParser()
        self.config.read(config_path, encoding='utf-8-sig')

    # database connection
    def get_connection(self):
        user = self.config.get('DB', 'user')
        password = self.config.get('DB', 'password')
        host = self.config.get('DB', 'host')    
        port = self.config.get('DB', 'port')
        database = self.config.get('DB', 'database')
        
        conn_url = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(user, password, host, port, database)
        return create_engine(conn_url, pool_size=20, max_overflow=50, pool_recycle=30)
        
    def get_ddl(self):
        engine = self.get_connection()
        sql = "SELECT table_name FROM all_tables"
        df = pd.read_sql_query(sql, engine)
        return df