# 这是付费路径的脚本
import geshou.data.userdata as gmdata
import pandas as pd
import numpy as np

# 计费点-付费次数-uid统计['proname','uid','order']
def pay_way():
    pay_user = gmdata.pay_users()
    pay_user = pay_user[pay_user['serverid'] >= 4550]

    # 按照计费点统计所有人数
    proname_all_user = pd.pivot_table(pay_user,index='proname',values='uid',aggfunc='count').reset_index()
    # 按照付费顺序，统计人数
    proname_first = pd.pivot_table(pay_user,index='proname',columns='order',values='uid',aggfunc='count').reset_index()

    # 两个表连接，['proname','uid','order']计费点，总人数，首充人数
    proname_order_count = pd.merge(proname_all_user,proname_first,how='left',on='proname').set_index('proname')

    return proname_order_count

# 和 pay_way() 表结构一样，但是值是在0-1之间,表示分布占比
def pay_way_radio():

    # 汇总付费次数
    proname_order_count_sum = pay_way().sum()
    # 再相除，得到比例，和 pay_way() 表结构一样，但是值是在0-1之间
    proname_order_count_radio = pay_way().div(proname_order_count_sum.T)
    return proname_order_count_radio




print(pay_way())