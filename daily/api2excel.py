import json
from urllib.request import Request,urlopen
import pandas as pd
from io import StringIO
import requests



url = "http://gsccsapi.legu.cc/api/?app=sinfo&owner=geshouccs"
#包装头部
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36'}

#构建请求
request = Request( url, headers= headers )
html = urlopen( request )
#获取数据
data = html.read().decode("utf-8")
data = data.replace('<br/>','\n')
# data = data.replace('&nbsp;&nbsp;',' ')

a = pd.read_csv(StringIO(data),sep='&nbsp;&nbsp;',header=None,names=['id','区服','date','owner'])

a['date'] = pd.to_datetime(a['date'],format='%Y/%m/%d')
a['days_diff'] = -(a['date'] - pd.to_datetime('today')).apply(lambda x: x.days)
print(a)

txt1 = a['区服'][a['days_diff'] == 28].values
txt2 = a['owner'][a['days_diff'] == 28].values
txt = '离明天有28天的区服：%s'%txt1 + '\n'+'渠道：%s'%txt2

def dingmessage(text):
# 请求的URL，WebHook地址
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=b29f1cbb75ba695880978a8f9212ccefcc89958455abb2d5cf5bc28211af4cc4"
#构建请求头部
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
}
#构建请求数据
    text
    message ={

        "msgtype": "text",
        "text": {
            "content": text
        },
        "at": {
            "isAtAll": True
        }

    }
#对请求的数据进行json封装
    message_json = json.dumps(message)
#发送请求
    info = requests.post(url=webhook,data=message_json,headers=header)
#打印返回的结果
    print(info.text)

dingmessage(txt)

