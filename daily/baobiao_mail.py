# 导入库
import yagmail

# 登录SMTP服务器
# user - 邮箱账号
# password - 邮箱登录授权码
# host - 邮箱SMTP服务器地址
yag = yagmail.SMTP(user = "2206525490@qq.com", password='nuasmlfsgywzebjd', host = 'smtp.qq.com')

# 编辑邮件内容
contents = [
    '自动报表邮件测试',
    'Here is a test mail!'
    ]

# 发送邮件
# to - 收信邮箱
# subject - 邮件主题
# contents - 邮件内容
yag.send(to = ['dengjie@legu.cc','lijun@legu.cc'], subject = '自动报表邮件测试', contents = contents)
