from chat2db.prompts import load_prompt
from chat2db.database.mydb import MySQLDB

#print(load_prompt("router"))

mysql_db = MySQLDB()
df = mysql_db.get_dummy()
print(df.head())



