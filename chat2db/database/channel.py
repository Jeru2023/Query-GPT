import configparser
import json
import os

from .db_connector import DbConnector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Channel():
    """
        调用时 传入channel即对应的db名字，然后可以获取当前channel所有的base数据
        database_schema_string: (表 + 列 + demo数据)
        functions: chat2db的function
        prompts:当前channel的prompts
        table_type：当前channel的表类型（view或者table）
        target_tables：指定的表名或者view名
    """

    def __init__(self, db_name, ini=os.path.join(BASE_DIR, '../config/config.ini')):
        self.config = configparser.ConfigParser()
        self.config.read(ini, encoding="utf-8")
        self.db_name = db_name
        self.target_tables = json.loads(self.config.get(db_name, "tables"))
        self.table_type = self.config.get(db_name, "table_type")
        # self.channel_prompt = channel_obj.get_channel_prompt
        # self.base_prompt = channel_obj.get_base_prompt
        self.clickhouse_ = DbConnector(section=db_name)

    @property
    def database_schema_string(self):
        """
            Returns: 当前数据库的schema信息(表 + 列 + demo数据)
        """
        return "\n".join(
            [
                f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}\n Demo Data: {', '.join(table['demo_data'])}"
                for table in self.get_database_info()
            ]
        )

    @property
    def functions(self):
        """
        TODO: 读取 prompts/下面的prompts 生成每个channel的function
        Returns: functions
        """
        func = [
            {
                "name": "ask_database",
                "description": self.base_prompt['description'],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": self.base_prompt['prompt'],
                        }
                    },
                    "required": ["query"],
                },
            }
        ]
        return func

    def get_table_names(self):
        """Return a list of table names."""

        if self.table_type == 'View':
            tables = self.clickhouse_.click_read_sql(
                f"select name  from system.tables where engine='View'  and database = '{self.db_name}'")
        else:
            tables = self.clickhouse_.click_read_sql(
                f"select name  from system.tables where   database = '{self.db_name}'")
        return tables['name'].to_list()

    def get_column_names(self, table_name):
        """Return a list of column names."""
        df = self.clickhouse_.click_read_sql(
            f"select distinct name,type  from system.columns where database='{self.db_name}' and table='{table_name}' ")
        return [f"{name}({type})" for name, type in zip(df['name'], df['type'])  ]

    def get_database_info(self):
        """Return a list of dicts containing the table name and columns for each table in the database."""
        table_dicts = []
        for table_name in self.get_table_names():
            if table_name not in self.target_tables:
                continue
            columns_names = self.get_column_names(table_name=table_name)
            demo_data = self.get_table_demo_data(table_name=table_name)
            table_dicts.append({"table_name": table_name, "column_names": columns_names, "demo_data": demo_data})
        return table_dicts

    def get_table_demo_data(self, table_name):
        """
        获取表格的一条原始数据
        :return:
        """
        data = self.clickhouse_.click_read_sql(
            f"select  * from {table_name} limit 1 ")
        ls = []
        for item in data.to_dict(orient='records'):
            for k, v in item.items():
                ls.append(f'字段[{k}]的demo数据为[{v}]')
        return ls


if __name__ == '__main__':
    channel = Channel(db_name='tmall_pc')
    # print(channel.get_column_names('ai_tmall_pc'))
    print(channel.database_schema_string)
