import requests


# 网站登陆获取cookies
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
