from chat2db.prompts import load_prompt
from chat2db.database.mydb import MyDB

#print(load_prompt("router"))

mydb = MyDB()
df = mydb.get_dummy()
print(df.head())



