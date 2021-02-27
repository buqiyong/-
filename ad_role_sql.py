import psycopg2
from sshtunnel import SSHTunnelForwarder
import pandas as pd
import yagmail
import  numpy as np
from matplotlib import pyplot as plt

pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)

def zhiyou_connect():
    server = SSHTunnelForwarder(
        # 指定ssh登录的跳转机的address
        ssh_address_or_host=('47.110.87.82', 10022),
        ssh_username='cxh',
        # 设置密钥
        # ssh_pkey='私钥文件全路径',
        ssh_password='2020@zy',

        # 设置数据库服务地址及端口
        remote_bind_address=('localhost', 5432))
    server.start()
    conn = psycopg2.connect(database='berry',
                            user='dev',
                            password='',
                            host='127.0.0.1',  # host、port 固定
                            port=server.local_bind_port)
    return conn
conn = zhiyou_connect()

def df_role_ad():
    sql = """
    SELECT
    日期,
    count(qq.role_id)as 参与角色,
    sum(qq.总发起订单)as 总发起订单,
    sum(qq.成功订单)as 总成功订单


    FROM
    	(SELECT
    	b.role_id,
    	(a.created_at :: date)as 日期,
    	COUNT(a."id")as 总发起订单,
    	COUNT(case WHEN a.status = 2 then a."id" END)as 成功订单

    	FROM
    	incentive_ad_orders a

    	LEFT JOIN
    	incentive_role_snapshots b
    	ON
    	a."id" = b."id"

    	GROUP BY
    	b.role_id,
    	日期)qq

    GROUP BY
    日期

    ORDER BY
    日期


    """
    df_role_ad = pd.read_sql(sql, conn)
    df_role_ad['单客发起'] =df_role_ad.总发起订单 /df_role_ad.参与角色
    df_role_ad['完播率'] =df_role_ad.总成功订单 /df_role_ad.总发起订单
    df_role_ad[['参与角色','总发起订单','总成功订单']] = df_role_ad[['参与角色','总发起订单','总成功订单']].astype('int')
    # df_role_ad['单客发起'] = df_role_ad['单客发起'].round(2)
    # df_role_ad['完播率'] = df_role_ad['完播率'].apply(lambda  x:format(x,'.2%'))
    return df_role_ad
def df_user_login():
    sql2 = """
    select
    DISTINCT
    a1."登录时间",
    count(distinct(u.name)) as 当天登录用户

    from
    users u

    LEFT JOIN
    roles r
    on
    r.user_id = u."id"

    LEFT JOIN
    (select
    user_id as uid,
    logged_at :: date as 登录时间
    from
    user_logins)a1
    on
    a1.uid = u.id


    WHERE
    r.game_id = 4
    and
    r.spkg_id in(38,36,29,28,30)
    and
    u.costs <=1200
    and
    a1."登录时间" is not null

    GROUP BY
    a1."登录时间"
    """

    df_user_login = pd.read_sql(sql2, conn)
    return df_user_login
def ad_overview(df_role_ad, df_user_login):
    ad_overview = pd.merge(df_role_ad, df_user_login, how='left', left_on='日期', right_on='登录时间')
    del ad_overview['登录时间']
    ad_overview['参与率'] = (ad_overview.参与角色 / ad_overview.当天登录用户)
    order = ['日期', '当天登录用户', '参与角色', '参与率', '总发起订单', '总成功订单','单客发起', '完播率']
    ad_overview = ad_overview[order]
    return ad_overview

df_role_ad =df_role_ad()
df_user_login=df_user_login()
ad_overview_list = ad_overview(df_role_ad,df_user_login)

print(ad_overview_list,'\n')

# ad_overview.to_excel("角色广告.xlsx",index=False)




def 完播标准阈(min_role):
    throw_min_role = ad_overview_list.iloc[ad_overview_list[ad_overview_list["参与角色"] >= min_role].index]["完播率"]
    完播历史标准阈值 = np.median(throw_min_role)
    过去七天标准阈值 = np.mean(throw_min_role.iloc[-9:-2])
    return [完播历史标准阈值,过去七天标准阈值]

完播指标=完播标准阈(15)
print(完播指标)
def 比较判断(判断值,参考值,q,n):
    x = (判断值-参考值)/参考值
    y = None
    if -0.3< x< -0.1:
        y = "昨日%s较%s：下降"%(q,n)
    elif x <= -0.3:
        y = "昨日%s较%s：大幅下降"%(q,n)
    elif x > 0.1:
        y = "昨日%s较%s：提升"%(q,n)
    elif x > 0.3:
        y = "昨日%s较%s：大幅提升"%(q,n)
    else:
        y= "昨日%s较%s：正常波动"%(q,n)
    return y

历史完播结论=比较判断(ad_overview_list.完播率.iloc[-2],完播指标[0],'完播率',"历史完播标准")
最近7天完播结论=比较判断(ad_overview_list.完播率.iloc[-2],完播指标[1],'完播率',"最近7天完播标准")
print(历史完播结论)


ad_overview_list.to_excel('表格.xlsx')



def email(to_adress,title,contents):
    yag = yagmail.SMTP(user='mokerchen@foxmail.com', password="nuasmlfsgywzebjd", host='smtp.qq.com')
    yag.send(to=to_adress, subject=title, contents=contents)
email_adress =[
    'hongmeigui98vk@dingtalk.com',
    'iim8580@dingtalk.com',
    'mjv3081@dingtalk.com'
]
title = "广告数据分析日报"
contents = [历史完播结论,最近7天完播结论,'C:\\Users\\Administrator\\PycharmProjects\\untitled\\表格.xlsx']

email(email_adress,title,contents)
# server.close()




