import configparser
from clickhouse_driver import Client
import pandas as pd
import re
import os
import pymysql
from sqlalchemy import create_engine
from urllib.parse import quote_plus as urlquote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class DbConnector(object):

    def __init__(self, ini=os.path.join(BASE_DIR, '../config/config.ini'), section='clickhouse'):  # section来选择服务器
        self.section = section
        self.config = configparser.ConfigParser()
        self.config.read(ini, encoding="utf-8")
        self.host = self.config.get(section, "host")
        self.password = self.config.get(section, "password")
        self.user = self.config.get(section, "user")
        self.database = self.config.get(section, "database")
        self.port = int(self.config.get(section, "port"))

    def click_con(self):
        return Client(host=self.host,
                      user=self.user, password=self.password,
                      database=self.database)

    def get_config(self, section):
        sql = self.config.get(section, "sql")
        res = self.click_read_sql(sql)
        return res

    def click_read_sql(self, sql):
        client = self.click_con()
        data, columns = client.execute(sql, columnar=True, with_column_types=True)
        df = pd.DataFrame({re.sub(r'\W', '_', col[0]): d for d, col in zip(data, columns)}, dtype=str)
        return df

    def click_type_dict(self, tb_name):
        sql = f"select name, type from system.columns where table='{tb_name.split('.')[1]}';"
        df = self.click_read_sql(sql)
        df = df.set_index('name')
        type_dict = df.to_dict('dict')['type']
        return type_dict

    def mysql_con(self):
        con = pymysql.connect(host=self.host, user=self.user, password=self.password,
                              database=self.database, port=self.port)
        return con

    def mysql_read_sql(self, sql):
        con = self.mysql_con()
        df = pd.read_sql(sql, con=con)
        return df

    def mysql_get_config(self, section):
        sql = self.config.get(section, "sql")
        res = self.mysql_read_sql(sql)
        return res



if __name__ == '__main__':
    cc = DbConnector(section='tmall_pc')
    x = cc.click_read_sql("show tables;")
    print(x)
