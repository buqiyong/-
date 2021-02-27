import pymysql

def my_conn(database):
    conn = pymysql.connect('localhost',user = "root",passwd = "legu123",db = database)
    return conn

def gm():
    conn = pymysql.connect(host="v3.legu.cc", user='gamemana', passwd='asd123ds!@3dcxsxxss', db='gamemana',charset="utf8")
    return conn



