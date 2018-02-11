from CrawlerBase import CrawlerBase
import requests
from bs4 import BeautifulSoup
import threading
import time
import os
import abc  # 利用abc模块实现抽象类


class Crawler(CrawlerBase):
    lock = threading.RLock()
    # 最大下载线程数
    __max_thread_num = 5

    @property
    def max_thread_num(self):
        return self.__max_thread_num

    @max_thread_num.setter
    def max_thread_num(self, value):
        self.__max_thread_num = value
        print('设置最大下载线程数:', value)

    # 页面信息列表
    __page_info_list = []

    def append_page_info_list(self, value):
        self.__page_info_list.append(value)

    # 帖子信息列表
    __post_info_list = []
    # 下载文件信息列表
    __download_info_list = []
    # 线程池
    __thread_pool = []
    # 帖子下载线程
    __thread_post = None

    def __init__(self):

        CrawlerBase.__init__(self)

        print('Clawler 构造函数执行')
        # self.save_path = path
        print('Clawler 构造函数执行结束')

        return

    @abc.abstractmethod
    def on_gen_all_page(self, url, li):
        """
        自定义页面链接生成规则，加入列表
        :param url: 主链接
        :param li: list 作为参数
        :rtype:
        :return:
        """
        return

    @abc.abstractmethod
    def on_parse_page(self, soup):
        """
        自定义解析规则，解析页面找到每个帖子所在区块
        :param soup: BeautifulSoup
        :rtype:
        :return:
        """
        childs = None
        return childs

    @abc.abstractmethod
    def on_parse_page_child(self, child):
        """
        自定义解析规则, 从页面解析帖子链接信息
        :param child:
        :rtype:
        :return:
        """
        new_info = None
        return new_info

    @abc.abstractmethod
    def on_parse_post(self, soup):
        """
        自定义解析规则，解析帖子找到每个下载区块
        :param soup: BeautifulSoup
        :rtype:
        :return:
        """
        childs = None
        return childs

    @abc.abstractmethod
    def on_parse_post_child(self, child, info, index):
        """
        自定义解析规则, 从帖子解析下载链接信息
        :param child:
        :param info:
        :param index:
        :rtype:
        :return:
        """
        new_info = None
        return new_info

    @abc.abstractmethod
    def on_down_file(self, info):
        """
        下载预处理接口,从info提取数据返回链接和文件名
        :param info: 下载文件相关信息
        :rtype:
        :return:
        """
        url = ''
        name = ''
        return {'url': url, 'name': name}

    def set_url(self, url):
        """
        设置主链接
        :param url:
        :rtype:
        :return:
        """
        super().set_url(url)

        # 设置的链接加入页面链接列表
        if url != '':
            self.__page_info_list.append({'url': url})

        return

    def __parse_page_child(self, child):
        """
        从页面解析一个帖子信息并且添加入列表
        :param child:
        :rtype:
        :return:
        """
        d = self.on_parse_page_child(child)

        if d is None:
            return

        self.lock.acquire()
        self.__post_info_list.append(d)
        self.lock.release()

        return

    def __parse_page(self, page_url):
        """
        解析页面找到每个帖子区块
        :param page_url:
        :rtype:
        :return:
        """
        r = requests.get(page_url, cookies=self.cookies)
        r.encoding = self.encoding
        print("子页面链接:[%s]" % r.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # 根据规则找到包含下载文件链接的子节点列表
        childs = self.on_parse_page(soup)
        if childs is None:
            return

        for child in childs:
            self.__parse_page_child(child)

        return

    def __parse_post_child(self, child, info, index):
        """
        从帖子解析下载链接信息并且添加入列表
        :param child:
        :rtype:
        :return:
        """
        d = self.on_parse_post_child(child, info, index)

        if d is None:
            return

        self.lock.acquire()
        self.__download_info_list.append(d)
        self.lock.release()
        return

    def __parse_post(self):
        """
        解析帖子找到每个下载区块
        :param:
        :rtype:
        :return:
        """
        self.lock.acquire()
        info = self.__post_info_list.pop(0)
        self.lock.release()
        r = requests.get(info['url'], cookies=self.cookies)
        r.encoding = self.encoding
        print("帖子链接:[%s]" % r.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # 根据规则找到包含下载文件链接的子节点列表
        childs = self.on_parse_post(soup)
        if childs is None:
            return

        index = 0
        for child in childs:
            index += 1
            self.__parse_post_child(child, info, index)

        return

    def __down_file(self):
        """
        下载列表位置0的文件
        :param:
        :rtype:
        :return:
        """
        self.lock.acquire()
        info = self.__download_info_list.pop(0)
        self.lock.release()

        rlt = self.on_down_file(info)
        if rlt is None:
            return False

        file_url = rlt['url']

        if os.path.isdir(self.save_path) == 0:
            os.makedirs(self.save_path)
        file_name = str(self.save_path) + rlt['name']

        # '''
        try:
            req = requests.get(file_url)  # create HTTP response object
            with open(file_name, 'wb') as f:
                f.write(req.content)
        except:
            print('*** 下载失败 *** [%s] 文件名:' % file_url, file_name)
        else:
            print('下载成功 [%s] 文件名:' % file_url, file_name)
        finally:
            pass
        # '''

        # time.sleep(0.2)

        return True

    def down_thread(self, mode):
        if self.__max_thread_num + 1 > threading.active_count():
            time.sleep(0.1)
            print("线程个数:[%d] 页面队列:[%d] 帖子队列:[%d] 下载队列:[%d]" % (
                self.__max_thread_num, len(self.__page_info_list), len(self.__post_info_list),
                len(self.__download_info_list)))
            # 清除失效线程池
            i = 0
            num = len(self.__thread_pool)
            while i < num:
                if self.__thread_pool[i].isAlive():
                    i += 1
                else:
                    del self.__thread_pool[i]
                    num -= num

            if mode == 'post':
                if self.__thread_post is None:
                    self.__thread_post = threading.Thread(target=self.__parse_post)
                    self.__thread_post.start()
                elif self.__thread_post.isAlive():
                    pass
                else:
                    self.__thread_post = threading.Thread(target=self.__parse_post)
                    self.__thread_post.start()
            else:
                self.__thread_pool.append(
                    threading.Thread(target=self.__down_file))
                self.__thread_pool[-1].start()
            pass
        return

    def deal_down_list(self):
        flg = False
        while True:
            self.lock.acquire()
            down_num = len(self.__download_info_list)
            self.lock.release()
            if down_num > 0:
                flg = False
                self.down_thread('file')
            elif len(self.__post_info_list) > 0:
                flg = False
                self.down_thread('post')
            else:
                if flg:
                    pass
                else:
                    flg = True
                    self.__parse_page(self.__page_info_list.pop(0)['url'])


    def gen_all_page(self, *args):
        """
        自定义页面链接生成规则，加入列表
        :param li: list 作为参数
        :rtype:
        :return:
        """
        if self.url == "":
            return

        # 进行了页面生成就清空原队列
        self.__page_info_list.clear()

        self.on_gen_all_page(*args)

        return
