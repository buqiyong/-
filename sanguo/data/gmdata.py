import pandas as pd
import daily.mysql as mysql
import numpy as np
import datetime
import time
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', None)
np.set_printoptions(suppress=True)
gm = mysql.gm()

# 所有付费数据 ['ctime','serverid','uid','proname','money','order','time_diff']
def pay():
    sql = """
    SELECT
        ctime,
        serverid,
        uid,
        proname,
        money
    FROM
        gm_game_paylist
    WHERE
        game = 'huixie' 
        """
    df = pd.read_sql(sql,con=gm)

    # 按照时间顺序，记录付费的顺序
    df['order'] = df.groupby('uid')['ctime'].rank(ascending=True, method='first')

    # 用shift方法，把['ctime']向下移动一位，必须转int，不然科学计数法看不懂
    shift = df.groupby('uid')['ctime'].shift().fillna(0).astype('int64')
    # 距离上次付费的时间差，秒
    df['time_diff'] = df['ctime']-shift
    # 大于1年的，删
    df['time_diff'] = df['time_diff'].copy().apply(lambda x:None if x >= 31536000 else x)


    return df

# 所有的用户信息['uid','owner','channel','lv','ctime','lastlogintime']
def user_info():
    sql = """
    SELECT
        uid,
        owner,
        channel,
        lv,
        ctime,
        lastlogintime

    FROM
        `gm_game_user`

    WHERE
        game = 'huixie'
    """
    df = pd.read_sql(con=gm, sql=sql)

    # df['ctime'] = pd.to_datetime(df['ctime'].values, utc=True, unit='s').tz_convert("Asia/Shanghai")
    # df['ctime'] = df['ctime'].dt.date.astype('datetime64[ns]')
    # 转北京时间的方法

    return df

# 所有三国【付费】用户vip数据 ['uid','sum_pay','vip']，没有付费的用户是不在这里面的！！注意！！
def pay_sum_vip():
    sql = """
    SELECT
        uid,
        sum(money) as sum_pay,
        CASE 
            WHEN sum(money)<3000 THEN 1
            WHEN sum(money)<10000 THEN 2
            WHEN sum(money)<20000 THEN 3
            WHEN sum(money)<50000 THEN 4
            WHEN sum(money)<100000 THEN 5
            WHEN sum(money)<150000 THEN 6
            WHEN sum(money)<200000 THEN 7
            WHEN sum(money)<300000 THEN 8
            WHEN sum(money)<500000 THEN 9
            WHEN sum(money)<1000000 THEN 10
            WHEN sum(money)<1500000  THEN 11
            WHEN sum(money)<3000000  THEN 12
            WHEN sum(money)<5000000  THEN 13
            WHEN sum(money)<9000000  THEN 14
            WHEN sum(money)<14000000  THEN 15
            WHEN sum(money)<20000000  THEN 16
            WHEN sum(money)>=20000000  THEN 17
        ELSE
            0
        END 'vip'
    FROM
        gm_game_paylist
    WHERE
        game = 'huixie' 
    GROUP BY
        uid
        """
    df = pd.read_sql(sql,con=gm)
    return df

# 所有三国付费用户的数据
# ['paytime','serverid','uid','proname','money','order','time_diff','sum_pay','vip','owner','channel','lv','ctime','lastlogintime','created_time_diff','lastlogin_time_diff']
def pay_users():

    data = pd.merge(pay(),pay_sum_vip(),how='left',on='uid')
    # 把pay的支付时间字段 改为 paytime
    data = data.rename(columns={'ctime':'paytime'})
    # 再链接用户信息
    data = pd.merge(data,user_info(),on='uid',how='left')

    # # 支付时间戳 转成datetime,时区改成上海
    # data['paytime'] = pd.to_datetime(data['paytime'].values, utc=True, unit='s').tz_convert("Asia/Shanghai")
    # # 注册时间戳 转成datetime,时区改成上海
    # data['ctime'] = pd.to_datetime(data['ctime'].values, utc=True, unit='s').tz_convert("Asia/Shanghai")
    # # 最后登录时间戳 转成datetime,时区改成上海
    # data['lastlogintime'] = pd.to_datetime(data['lastlogintime'].values, utc=True, unit='s').tz_convert("Asia/Shanghai")

    # 本次支付时间，距离注册时间的时间差
    data['created_time_diff'] = data['paytime']-data['ctime']
    # 本次支付时间，距离最后登录时间的时间差
    data['lastlogin_time_diff'] = data['lastlogintime'] - data['ctime']

    return data

# 首充计费点['ctime','uid','serverid','proname','money'],只用到首冲
def first_pay():
    # sql 查找最早的付费时间
    frist_paytime_sql = """
    SELECT
        min(ctime) as ctime,
        uid
    from
        gm_game_paylist 
    WHERE
        game = 'huixie' 
    GROUP BY
        uid
    """

    frist_pay_date = pd.read_sql(frist_paytime_sql,con=gm)

    # merge 所有的付费信息
    frist_pay = pd.merge(frist_pay_date,pay(),on=['ctime','uid'])
    return frist_pay

# 用户登录信息，给开始和结束时间 ['serverid','uid','cdate','logintimes','sum_pay','vip','owner','channel','lv','ctime','lastday_diff']
def login(a,b):
    sql = f"""
    SELECT
        `serverid`,
        `uid`,
        cdate,
        logintimes
    FROM
        `gm_game_login` 
    WHERE
        `game` = 'huixie' 
    AND cdate BETWEEN '{a}' and '{b}'
    
    ORDER BY
        `uid`,
        cdate
    """
    lg = pd.read_sql(sql, con=gm)
    lg['cdate'] = lg['cdate'].astype('datetime64[ns]')

    df = pd.merge(lg,pay_sum_vip(),how='left',on='uid')
    # 必须把没有vip信息的用0填充
    df['vip'] = df['vip'].fillna(0)
    df = pd.merge(df,user_info(),how='left',on='uid')

    df['lastday_diff'] = df.groupby('uid')['cdate'].diff()
    #距离上次登录的时间差
    return df

# 新增用户信息 ['serverid','uid','owner','channel','lv','ctime','sum_pay','vip','fp_proname','fp_money']
def created(a,b):
    sql = f"""
    SELECT
        serverid,
        uid,
        owner,
        channel,
        lv,
        from_unixtime(ctime,'%Y-%m-%d')as ctime

    FROM
        `gm_game_user`

    WHERE
        game = 'huixie'
    and 
        from_unixtime(ctime,'%Y-%m-%d') between '{a}' and '{b}'
    """
    df = pd.read_sql(con=gm, sql=sql)
    df = pd.merge(df,pay_sum_vip(),on='uid',how='left')
    df = pd.merge(df,first_pay().loc[:,['uid','proname','money']],on='uid',how='left')
    df = df.rename(columns={'proname':'fp_proname','money':'fp_money'})
    return df

# 日期列表生成方法
def get_date_list(begin_date, end_date):
    date_list = [x.strftime('%Y-%m-%d') for x in list(pd.date_range(start=begin_date, end=end_date))]
    return date_list

print(pay_users())

# pay_users().to_excel('C:\\Users\\mayn\\Desktop\\歌手\\数据分析\\诙谐付费用户.xlsx')

