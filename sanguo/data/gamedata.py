import pandas as pd
import json
import demjson

hero = pd.read_csv('F:\\huixieFile\\csv2json\\csv\\hero.csv',encoding='GB18030')
item = pd.read_csv('F:\\huixieFile\\csv2json\\csv\\item.csv',encoding='GB18030')
shenqilv = pd.read_csv('F:\\huixieFile\\csv2json\\csv\\shenqilv.csv',encoding='GB18030')
event = pd.read_excel('C:\\Users\\mayn\\Desktop\\三国\\字段.xlsx')
pay = pd.read_json('F:\\huixieFile\\server\\json\\pay.json')

attr = {
    "useexp": '英雄经验',
    "exp": '玩家经验',
    "jinbi": '铜钱',
    "rmbmoney": '元宝',
    "jifen": '悬赏积分'
}



