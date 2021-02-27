import pandas as pd
import json
import demjson


csv = pd.read_csv('C:\\Users\\mayn\\Desktop\\歌手\\data\\4510_5f2a426c077b0521c7b9366a.csv')

data = csv.iloc[:,1]

list1 = []

# print(data)

for i in data:
    dc = json.loads(i)
    # print(dc)
    if 'prize' in dc.keys():
        d1 = dc['prize']
        if int(len(d1)) == 2:
            d2 = int(d1[1]['n'])
            # print(d2)
        values = pd.DataFrame(dc['prize'])
        list1.append(d2)



print('24小时总量：',sum(list1)*1000)

print('最大时间：',max(list1)*1000/21168216/60/60,'小时')

print('秒赚时间：',sum(list1)*1000/21168216/60/60,'小时')

# delete_hero = pd.concat(list1)
#
#
# print(delete_hero)

# csv.to_excel('C:\\Users\\mayn\\Desktop\\lianhuan.xlsx')


