# 这是分析竞拍分红 和 合同交易的脚本

import geshou.data.userdata as gmdata
import pandas as pd
import json
import demjson

excel_reader=pd.ExcelFile('E:\\歌手\\竞拍_合同\\竞拍_合同_0926_1011.xlsx')  # 指定文件
sheet_names = excel_reader.sheet_names  # 读取文件的所有表单名，得到列表
# print(sheet_names)

# 读取表单的内容，i是表单名的索引，等价于pd.read_excel('文件.xlsx', sheet_name=sheet_names[i])
jysj_data = excel_reader.parse(sheet_name='交易合同上架状态') # ['uid','jiaoyi_shangjia']
jytimes_data = excel_reader.parse(sheet_name='交易次数')   # ['cdate','uid','jiaoyi_num']
pmfh_data = excel_reader.parse(sheet_name='分红领奖')   # ['cdate','uid','jingpai_fh','laiyuan']
pmcj_data = excel_reader.parse(sheet_name='竞拍出价')   # ['cdate','uid','how','prize']

# 统计交易合同,平均参与次数，平均参与率
# 传日活时间,返回 jyht_pivot ，['vip','jiaoyi_num','join_participation']
# 分两种情况，传how = 'new' 的时候,可以带上注册时间，看一部分用户的情况
def jyht_pivot(a,b,how='',new_stime='',new_etime = ''):

    # 统计每天交易次数的和，因为王能鹏导出的数据源有重复的，必须除以2
    jyht_join_times = jytimes_data.groupby(['cdate','uid'])['jiaoyi_num'].sum()/2
    # 重置索引
    jyht_join_times = jyht_join_times.reset_index()
    # 链接总充值、vip数据
    jyht_join_times = pd.merge(jyht_join_times,gmdata.pay_sum_vip(),how='left',on='uid').fillna(0)
    # 链接用户信息 最后得到['cdate','uid','jiaoyi_num','sum_pay','vip','owner','channel','lv','ctime']
    jyht_join_times = pd.merge(jyht_join_times,gmdata.user_info(),how='left',on='uid').fillna(0)

    # 调用login方法,每天登录的人
    login = gmdata.login(a,b)


    # 如果传了一个 'new',就根据(new_stime,new_etime)，筛选出新用户的的参与
    if how == 'new':
        # 调用时间列表生成方法,生成新用户注册时间
        created_times = gmdata.get_date_list(new_stime,new_etime)

        # 筛选新用户的参与情况
        jyht_join_times = jyht_join_times[jyht_join_times['ctime'].isin(created_times)]

        # 统计新用户每天登录的vip
        login_vip_count = pd.pivot_table(login[login['ctime'].isin(created_times)], index='vip', columns='cdate', values='uid',aggfunc='count').fillna(0)
    else:
        # 统计全部用户每天登录的vip
        login_vip_count = pd.pivot_table(login, index='vip', columns='cdate', values='uid',aggfunc='count').fillna(0)


    # 交易合同，平均每天参与次数['vip','jiaoyi_num']
    jyht_join_times_mean = pd.pivot_table(jyht_join_times,index='vip',values='jiaoyi_num',aggfunc='mean').fillna(0)
    # 交易合同，每天参与人数数['vip','cdate']
    jyht_join_users_count = pd.pivot_table(jyht_join_times,index='vip',columns='cdate',values='uid',aggfunc='count').fillna(0)


    # 交易合同，每天参与率
    jyht_join_percent = (jyht_join_users_count / login_vip_count).T.mean().T.reset_index()
    jyht_join_percent.columns = ['vip','join_participation']

    # 最后参与次数与参与率合并，['vip','jiaoyi_num','join_participation']
    jyht_pivot = pd.merge(jyht_join_times_mean,jyht_join_percent,how='left',on='vip')

    return jyht_pivot

# 参与过合同交易的，合同当前上架状态
def jyht_sj():
    data = pd.merge(jysj_data, gmdata.pay_sum_vip(), how='left', on='uid').fillna(0)
    df = pd.pivot_table(data,index='vip',columns='jiaoyi_shangjia',aggfunc='count',values='uid')
    return df

# 拍卖的分析，方法和合同交易类似,也可以指定新用户
def paimai(a,b,how='',new_stime='',new_etime = ''):
    # 统计每天拍卖的人，在跨服和本服情况下的出价次数
    pm_join_times = pmcj_data.groupby(['cdate','uid','how'])['prize'].count()
    # 重置索引
    pm_join_times = pm_join_times.reset_index()
    # 链接总充值、vip数据
    pm_join_times = pd.merge(pm_join_times,gmdata.pay_sum_vip(),how='left',on='uid').fillna(0)
    # 链接用户信息 最后得到['cdate','uid','prize','sum_pay','vip','owner','channel','lv','ctime']
    pm_join_times = pd.merge(pm_join_times,gmdata.user_info(),how='left',on='uid').fillna(0)

    # 调用login方法,每天登录的人
    login = gmdata.login(a,b)


    # 如果传了一个 'new',就根据(new_stime,new_etime)，筛选出新用户的的参与
    if how == 'new':
        # 调用时间列表生成方法,生成新用户注册时间
        created_times = gmdata.get_date_list(new_stime,new_etime)

        # 筛选新用户的参与情况
        pm_join_times = pm_join_times[pm_join_times['ctime'].isin(created_times)]

        # 统计新用户每天登录的vip
        login_vip_count = pd.pivot_table(login[login['ctime'].isin(created_times)], index='vip', columns='cdate', values='uid',aggfunc='count').fillna(0)
    else:
        # 统计全部用户每天登录的vip
        login_vip_count = pd.pivot_table(login, index='vip', columns='cdate', values='uid',aggfunc='count').fillna(0)


    # 拍卖，平均每天参与次数['vip','prize']
    pm_join_times_mean = pd.pivot_table(pm_join_times,index='vip',values='prize',aggfunc='mean').fillna(0)
    # 拍卖，每天参与人数数['vip','cdate']
    pm_join_users_count = pd.pivot_table(pm_join_times,index='vip',columns='cdate',values='uid',aggfunc='count').fillna(0)


    # 交易合同，每天参与率
    pm_join_percent = (pm_join_users_count / login_vip_count).T.mean().T.reset_index()
    pm_join_percent.columns = ['vip','join_participation']

    # 最后参与次数与参与率合并，['vip','jiaoyi_num','join_participation']
    pm_pivot = pd.merge(pm_join_times_mean,pm_join_percent,how='left',on='vip')

    return pm_pivot



# 新增用户的交易合同参与，0930-1003
新用户合同互换 = jyht_pivot(a='2020-09-30',b='2020-10-11',how='new',new_stime='2020-09-30',new_etime='2020-10-03')
全部用户合同互换 = jyht_pivot(a='2020-09-26',b='2020-10-11')
参与拍卖用户当前上架状态 = jyht_sj()
新用户拍卖 = paimai(a='2020-09-30',b='2020-10-11',how='new',new_stime='2020-09-30',new_etime='2020-10-03')
全部用户拍卖 = paimai(a='2020-09-26',b='2020-10-11')


def to_excel(*args):
    import datetime

    xlsx = pd.ExcelWriter("C:\\Users\\mayn\\Desktop\\歌手\\数据分析\\合同交换 & 集团竞拍%s.xlsx"%str(datetime.date.today()))

    新用户合同互换.to_excel(xlsx, sheet_name="新用户合同互换",index=False)
    全部用户合同互换.to_excel(xlsx, sheet_name="全部用户合同互换",index=False)
    参与拍卖用户当前上架状态.to_excel(xlsx, sheet_name="参与拍卖用户当前上架状态",index=False)
    新用户拍卖.to_excel(xlsx, sheet_name="新用户拍卖",index=False)
    全部用户拍卖.to_excel(xlsx, sheet_name="全部用户拍卖",index=False)

    print("保存完成")
    xlsx.close()

to_excel()


