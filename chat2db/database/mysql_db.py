import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import configparser as cp
from urllib.parse import quote_plus as urlquote
 

class MySQLDB:
    def __init__(self, config_path='./chat2db/config/sphinx.config'):
        self.config_path = config_path
        self.config = cp.ConfigParser()
        self.config.read(config_path, encoding='utf-8-sig')

    # database connection
    def get_engine(self):
        user = self.config.get('DB', 'user')
        password = urlquote(self.config.get('DB', 'password'))

        host = self.config.get('DB', 'host')    
        port = self.config.get('DB', 'port')
        database = self.config.get('DB', 'database')
        
        conn_url = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(user, password, host, port, database)
        return create_engine(conn_url, pool_size=20, max_overflow=50, pool_recycle=30)
        
    def get_dummy(self):
        engine = self.get_engine()
        conn = engine.connect()

        sql = text("select count(*) from stock_code")
        df = pd.read_sql_query(sql, conn)
        return df