import requests
from bs4 import BeautifulSoup

'''
# 网站登陆获取cookies
# http://www.3ajiepai.com/member.php
def log_in(url, name, password):
    payload = {
        'mod': 'logging',
        'action': 'login',
        'loginsubmit': 'yes',
        'infloat': 'yes',
        'lssubmit': 'yes',
        'inajax': '1'
    }
    headers = {
        'Cache-Control': 'max-age=0',
        'Origin': 'http://www.3ajiepai.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://www.3ajiepai.com/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    data = {
        'fastloginfield': 'username',
        'username': name,
        'password': password,
        'quickforward': 'yes',
        'handlekey': 'ls'
    }

    session = requests.session()

    r = session.post(url, params=payload, headers=headers, data=data)
    print('login.text:', r.text)

    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    print(r.status_code)
    if r.status_code == 200:
        print('cookies:', cookies)
        return cookies
    else:
        return


# 登陆网站
log_in('http://www.3ajiepai.com/member.php', 'zjicbc', 'Yi7910ck')
'''

# 武当山庄

session = requests.session()

r = session.post('http://www.wdsz.net/thread-htm-fid-438.html')
r.encoding = 'GBK'
# print('login.text:', r.text)
soup = BeautifulSoup(r.text, 'html.parser')
childs = soup.find_all('input', type="hidden")
value = childs[0]['value']

ck = requests.session()

r = ck.post('http://www.wdsz.net/ck.php?nowtime=1518576091010')
with open('./img/ck.gif', 'wb') as f:
    f.write(r.content)

ckinput = input("请输入验证码:")
print("验证码:", ckinput)


def log_in(url, name, password):
    headers = {
        'Cache-Control': 'max-age=0',
        'Origin': 'http://www.3ajiepai.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://www.3ajiepai.com/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    data = {
        'verify': value, 'lgt': '0', 'pwuser': name, 'pwpwd': password, 'question': '0',
        'customquest': '', 'answer': '', 'gdcode': '673443', 'hideid': '0', 'forward': '',
        'jumpurl': 'http%3A%2F%2Fwww.wdsz.net%2Fthread.php%3Ffid-438.html', 'm': 'bbs', 'step': '2',
        'cktime': '31536000'
    }

    session = requests.session()

    r = session.post(url, data=data)
    print('login.text:', r.text)

    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    print(r.status_code)
    if r.status_code == 200:
        print('cookies:', cookies)
        return cookies
    else:
        return

# 登陆网站
log_in('http://www.wdsz.net/login.php?', 'wwwzj', 'zj8021')
