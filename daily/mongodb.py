import pymongo
import pandas as pd

# 账号密码方式连接MongoDB | "mongodb://用户名:密码@公网ip:端口/"
client = pymongo.MongoClient("mongodb://legugamedbreader:S9njEjsV6R4N4v@140.143.150.125:27017/")

# 指定数据库
s4030 = client.huixie_s4030
s4000 = client.huixie_s4000

# 指定集合
hero4030 = s4030.hero
hero4000 = s4000.hero

list1 = []

for i in hero4030.find({},{"_id":0,"uid":1,"color":1,"star":1,"lv":1}):
    # print(type(i))
    data = pd.DataFrame([i])
    list1.append(data)

for i in hero4000.find({},{"_id":0,"uid":1,"color":1,"star":1,"lv":1}):
    # print(type(i))
    data = pd.DataFrame([i])
    list1.append(data)

excel = pd.concat(list1)
print(excel)

excel.to_excel('C:\\Users\\mayn\\Desktop\\hero.xlsx')