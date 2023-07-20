import configparser
from clickhouse_driver import Client
import pandas as pd
import re
import os
import pymysql
from sqlalchemy import create_engine
from urllib.parse import quote_plus as urlquote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class connection_config(object):

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

    def click_save(self, df, tb_name):
        type_dict = self.click_type_dict(tb_name)
        # 类型处理
        for i in range(len(df.columns)):
            col_name = df.columns[i]
            col_type = type_dict[col_name]
            if 'Date' in col_type:
                df[col_name] = pd.to_datetime(df[col_name])
            elif 'Int' in col_type:
                df[col_name] = df[col_name].astype('int64')
            elif 'Float' in col_type:
                df[col_name] = df[col_name].astype('float')
            elif 'String' in col_type:
                df[col_name] = df[col_name].astype('str').fillna('')
        # df数据存入clickhouse
        cols = ','.join(df.columns)
        data = df.to_dict('records')
        client = self.click_con()
        client.execute(f"INSERT INTO {tb_name} ({cols}) VALUES", data, types_check=True)

    def click_execute(self, sql):
        client = self.click_con()
        client.execute(sql)

    def click_save_dict(self, dic, tb_name):
        df = pd.DataFrame([dic])
        self.click_save(df, tb_name)

    def mysql_con(self):
        con = pymysql.connect(host=self.host, user=self.user, password=self.password,
                              database=self.database, port=self.port)
        return con

    def mysql_read_sql(self, sql):
        con = self.mysql_con()
        df = pd.read_sql(sql, con=con)
        return df

    def mysql_save(self, df, tb_name):
        engine = create_engine(
            f'mysql+pymysql://{self.user}:{urlquote(self.password)}@{self.host}:{self.port}/{self.database}?charset=utf8mb4')
        # f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4')

        pd.io.sql.to_sql(df, name=tb_name.split('.')[-1], con=engine, if_exists='append', chunksize=100000, index=False)

    def mysql_get_config(self, section):
        sql = self.config.get(section, "sql")
        res = self.mysql_read_sql(sql)
        return res

    def mysql_execute(self, sql):
        con = self.mysql_con()
        cursor = con.cursor()
        cursor.execute(sql)
        con.commit()
        return cursor.rowcount

    def execute_many(self, sql, params):

        try:
            # self.reConnect()
            # self.cursor.executemany(sql, params)
            con = self.mysql_con()
            cursor = con.cursor()
            cursor.executemany(sql, params)
        except Exception as e:
            print(e)
            print(sql)
            print(params)
            return False
        else:
            con.commit()
            return True


if __name__ == '__main__':
    cc = connection_config(section='tmall_pc')
    x = cc.click_read_sql("show tables;")
    print(x)
