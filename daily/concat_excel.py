import pandas as pd
import os
import json

# 聚合一个xlsx下的多个sheet
def concat_sheet(sheet_to_concat='C:\\Users\\mayn\\Desktop\\三国\\data\\诙谐三国-砖石获取来源.xls'):
    data = pd.read_excel(sheet_to_concat,None)
    # 为了让表头可以读出来，一定要传一个None
    df_ls = data.keys()
    # 读取表头
    # print(df_ls)

    li = []
    for i in df_ls:
        li.append(data[i])
        # print(i)
    df = pd.concat(li)

    return df
    # a = data.to_json(orient='records')
    # print(a)

# 聚合一个文件夹下的多个文件，暂时只写了csv的，其他文件要改函数
def concat_file(file_to_concat = 'C:\\Users\\mayn\\Desktop\\歌手\\data'):
    list1 = []

    for info in os.listdir(file_to_concat):
        domain = os.path.abspath(r'C:\\Users\\mayn\\Desktop\\歌手\\data')  # 获取文件夹的路径
        info = os.path.join(domain, info)  # 将路径与文件名结合起来就是每个文件的完整路径
        data = pd.read_csv(info,parse_dates=True)
        print(data)
        list1.append(data)

    df = pd.concat(list1)
    return df

count = 0
df = pd.read_csv('C:\\Users\\mayn\\Desktop\\3500_5f0fcc5e56fec86cc7dcfadb.csv')
for i in df['数据'].values:
    a = json.loads(i)
    for k in a:
        if k == 'prize':
            count += 1
print(count)




