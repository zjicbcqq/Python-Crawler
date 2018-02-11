import re

class CrawlerBase:
    def __init__(self):
        print('CrawlerBase 构造函数执行')
        print('CrawlerBase 构造函数执行结束')
        return

    # 网站登陆cookies
    __cookies = None

    @property
    def cookies(self):
        return self.__cookies

    @cookies.setter
    def cookies(self, value):
        self.__cookies = value

    # 保存爬取文件的路径
    __save_path = ''

    @property
    def save_path(self):
        return self.__save_path

    @save_path.setter
    def save_path(self, value):
        str_len = len(value)

        # 路径末尾如果没有'/'补'/'
        if str_len > 0:
            if value[str_len - 1] != '/':
                value += '/'

        self.__save_path = value

    # 主链接
    __url = ''

    @property
    def url(self):
        return self.__url

    def set_url(self, value):
        """
        设置主链接
        :param value:
        :rtype:
        :return:
        """
        self.__url = value
        print('设置主链接:[%s]' % value)
        host = re.match('^((http://)|(https://))?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(/)',
                        value)
        if host is None:
            return
        self.__url_host = host.group()
        print('设置主域名:[%s]' % self.__url_host)

    # 主域名
    __url_host = ''

    @property
    def url_host(self):
        return self.__url_host

    # 编码
    __encoding = 'utf-8'

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, value):
        self.__encoding = value
