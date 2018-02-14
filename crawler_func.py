import requests
from bs4 import BeautifulSoup
import os
import subprocess
import re
import threading
import time

cookiesold = {
    '3nvN_7b26_auth': 'fc507Qk76p3hkwdqo8OYYIRm7LfVdlr1uLzZAazcNr5QcfOOMo%2BXaqSRuM9juSeKn7WWR6q87Gg3Yv28OcO9YfpnInw',
    '3nvN_7b26_checkfollow': '1', '3nvN_7b26_lastact': '1518073249%09member.php%09logging',
    '3nvN_7b26_lastcheckfeed': '227970%7C1518073249', '3nvN_7b26_lastvisit': '1518069649',
    '3nvN_7b26_lip': '58.62.52.111%2C1518073057', '3nvN_7b26_pc_size_c': '0', '3nvN_7b26_saltkey': 's5xE5LR2',
    '3nvN_7b26_sid': 'a92CL9', '3nvN_7b26_ulastactivity': '3f446m9k%2F3JqghhOTMXQfJ%2BJ8arjpUFb3F7DHMJ69x4MOPx5IyGa'}


def download_file(mode='requests', file_url='', filename=''):
    """
    下载指定文件
    :param mode:下载文件方式:requests(default),wget
    :param file_url:下载文件链接
    :param filename:保存的文件名(默认为链接文件名)
    :rtype: int
    :return: False:失败 True:成功
    """
    if file_url == '':
        return False

    if filename == '':
        # 获取链接文件名
        filename = os.path.basename(file_url)

    # 问号不能做文件名，需要替换
    filename = filename.replace('?', '9')

    if mode == 'requests':  # requests 下载方式
        req = requests.get(file_url)  # create HTTP response object
        with open(filename, 'wb') as f:
            f.write(req.content)
    elif mode == 'wget':  # wget 下载方式
        cmd = 'wget -O ' + filename + ' ' + file_url
        print('CMD:[%s]' % cmd)
        sub = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        print(sub.stdout.read())
    else:  # 其它模式待实现
        pass

    return True


def _get_name_from_atl(alt):
    """
    从"ABC_DEF_GHI"中提取DEF
    :param alt: 待提取字符串
    :rtype: str
    :return: 提取的字符串
    """
    title = ''
    s = alt.split('_')
    if len(s) > 2:
        for num in range(1, len(s) - 1):
            title += s[num]

    return title


def _get_date_from_url(url):
    """
    从页面链接提取年月日
    :param url:
    :rtype: str
    :return: 日期字符串(YYYYMMDD)
    """
    path = os.path.basename(url)
    li = path.split('-')
    date_str = '%04d%02d%02d' % (int(li[1]), int(li[2]), int(li[3]))
    # print(date_str)

    return date_str


def _down_page_file(url, cookies, prefix=''):
    """
    根据规则下载链接页面中的文件
    :param url: 链接
    :param cookies:
    :param prefix: 要保存的文件名前缀
    :rtype: None
    :return: 无
    """
    r = requests.get(url, cookies=cookies)
    print("parse url:%s" % r.url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # 根据规则找到包含下载文件链接的子节点列表
    childs = soup.find_all('img', onclick="zoom(this, this.src, 0, 0, 0)")

    # 当前正在下载的文件索引
    index = 0
    # 遍历子节点
    for c in childs:
        # 获取要保存的文件名，在alt关键字参数中
        alt = c.get('alt')
        # 获取下载链接，在file关键字参数中
        url = c.get('file')
        # file关键字参数不存在时，取src关键字
        if url is None:
            url = c.get('src')

        print("下载文件链接:[%s]" % url)
        name = _get_name_from_atl(alt)

        # 获取链接文件名
        url_name = os.path.basename(url)
        # 获取完整文件名
        file_name = prefix + '_' + name + '_' + url_name
        print("保存文件名称:[%s]" % file_name)
        index += 1
        print('正在下载:[%d/%d]' % (index, len(childs)))
        download_file('requests', url, 'img/' + file_name)

    return


def _thread_down_file_func(child, index, total, prefix):
    """
    在线程中进行文件下载(线程函数)
    :param child: 子节点
    :param index: 当前下载索引,显示作用
    :param total: 需要下载的文件数量
    :param prefix: 要保存的文件名前缀
    :rtype: None
    :return: 无
    """
    # 获取要保存的文件名，在alt关键字参数中
    alt = child.get('alt')
    # 获取下载链接，在file关键字参数中
    url = child.get('file')
    # file关键字参数不存在时，取src关键字
    if url is None:
        url = child.get('src')

    print("下载文件链接:[%s]" % url)
    name = _get_name_from_atl(alt)
    # 获取链接文件名
    url_name = os.path.basename(url)
    # 获取完整文件名
    file_name = prefix + '_' + name + '_' + url_name
    print("保存文件名称:[%s]" % file_name)
    index += 1
    print('线程[%s]正在下载:[%d/%d]' % (threading.current_thread().name, index, total))
    download_file('requests', url, 'img/' + file_name)

    return


def _down_page_file_thread(url, cookies, prefix='', thread_num=1):
    """
    根据规则下载链接页面中的文件(多线程)
    :param url: 链接
    :param cookies:
    :param prefix: 要保存的文件名前缀
    :param thread_num: 线程数(默认1)
    :rtype: None
    :return: 无
    """
    # 主线程占用1个线程,先加上
    thread_num += 1
    r = requests.get(url, cookies=cookies)
    print("子页面链接:[%s]" % r.url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # 根据规则找到包含下载文件链接的子节点列表
    childsall = soup.find_all('img', onclick="zoom(this, this.src, 0, 0, 0)")
    childs = childsall[0:1]


    # 当前正在下载的文件索引
    index = 0
    # 页面总共需要下载的文件索引
    total_num = len(childs)
    # 线程池列表
    thread_pool = []
    # 当前需要下载的文件数不为0,就继续下载
    while len(childs) > 0:
        # 当前激活线程数量少于设定线程数，就继续开启线程
        while (thread_num - threading.active_count()) > 0:
            # 当前需要下载的文件数为0，break
            if len(childs) == 0:
                break
            # 下载函数加入线程池
            thread_pool.append(
                threading.Thread(target=_thread_down_file_func, args=(childs.pop(0), index, total_num, prefix)))
            # 启动线程
            thread_pool[index].start()
            index += 1
    # 当前需要下载的文件数为0,就阻塞线程池所有线程,直到所有线程执行结束
    if len(childs) == 0:
        # 遍历线程池,阻塞线程
        for j in range(index):
            thread_pool[j].join()

    return


def _parse_date_page(url, cookies, page_num=0):
    """
    根据规则解析并下载某日某页页面内的所有子页面的文件。
    :param url: 当日页面链接
    :param cookies:
    :param page_num: 第几页
    :rtype: None
    :return: 无
    """
    if url == '':
        return

    # 获取日期
    date = _get_date_from_url(url)

    r = requests.get(url, cookies=cookies)
    print("当日某页页面链接:[%s]" % r.url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # 根据规则找到包含下载文件页面链接的子节点列表
    childs = soup.find_all('a', onclick="atarget(this)", class_="z")
    # 当前正在获取的子页面索引
    index = 0
    for c in childs:
        # 获取子页面链接，在href关键字参数中
        url = c.get('href')
        index += 1
        print('子页面链接:[%03d/%03d][%s]' % (index, len(childs), url))
        # 获取要保存的文件名前缀
        prefix = date + '_%02d_%03d' % (page_num, index)

        # 单线程下载
        # _down_page_file(url, cookies, prefix)

        # 多线程下载
        _down_page_file_thread(url, cookies, prefix, thread_num=5)

    return


def parse_all_date_page(url, cookies):
    """
    根据规则解析并下载某日所有页页面内的所有子页面的文件。
    :param url: 当日页面链接
    :param cookies:
    :rtype: None
    :return: 无
    """
    # 获取链接域名
    host = re.match('^((http://)|(https://))?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(/)', url)
    url_host = host.group()

    # 第一个链接加入列表
    url_list = [url]

    r = requests.get(url, cookies=cookies)
    print("当日页面链接:[%s]" % r.url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # 根据规则找到包含某日所有页页面链接的子节点列表
    childs = soup.find_all('a', string=re.compile('^[0-9]{1}$'), href=re.compile('archive-'))
    # print(childs)

    for c in childs:
        # 获取某页面链接，在href关键字参数中
        url = c.get('href')
        # 加入列表
        url_list.append(url_host + url)
    print(url_list)

    # 当前正要解析的某页页面索引
    index = 0
    for url in url_list:
        print("当日某页页面链接:[%s]" % url)
        index += 1
        _parse_date_page(url, cookies, index)

    return


def gen_pachong_cmd(url, year, month, end_date):
    """
    生成当日页面链接,供爬文件(1~31日)
    :param url: 当日页面链接
    :param year:
    :param month:
    :param end_date: 结束日
    :rtype: None
    :return: 无
    """
    u = url.split('-')
    for i in range(1, end_date + 1):
        print('parse_all_date_page(\'%s-%s-%s-%d-%s\', cookiesold)' % (u[0], year, month, i, u[4]))

    return


def gen_pachong_year_cmd(url, year):
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 1, 31)
    if year % 4 == 0:
        gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 2, 29)
    else:
        gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 2, 28)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 3, 31)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 4, 30)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 5, 31)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 6, 30)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 7, 31)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 8, 31)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 9, 30)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 10, 31)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 11, 30)
    gen_pachong_cmd('http://www.3ajiepai.com/archive-1980-1-31-1.html', year, 12, 31)

    return



# _down_page_file('http://www.3ajiepai.com/thread-5676-1-1.html', cookiesold, '2018')


# parse_date_page('http://www.3ajiepai.com/archive-2018-2-1-1.html', cookiesold)


# parse_all_date_page('http://www.3ajiepai.com/archive-2013-2-2-1.html', cookiesold)


# gen_pachong_cmd('http://www.3ajiepai.com/archive-2013-6-1-1.html', 2014, 1, 31)


# gen_pachong_year_cmd('http://www.3ajiepai.com/archive-2013-6-1-1.html', 2017)




# '''''
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-10-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-11-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-12-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-13-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-14-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-15-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-16-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-17-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-18-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-19-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-20-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-21-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-22-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-23-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-24-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-25-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-26-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-27-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-28-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-29-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-30-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-7-31-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-1-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-2-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-3-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-4-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-5-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-6-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-7-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-8-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-9-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-10-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-11-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-12-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-13-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-14-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-15-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-16-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-17-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-18-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-19-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-20-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-21-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-22-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-23-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-24-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-25-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-26-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-27-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-28-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-29-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-30-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-8-31-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-1-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-2-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-3-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-4-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-5-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-6-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-7-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-8-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-9-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-10-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-11-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-12-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-13-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-14-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-15-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-16-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-17-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-18-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-19-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-20-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-21-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-22-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-23-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-24-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-25-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-26-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-27-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-28-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-29-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-9-30-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-1-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-2-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-3-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-4-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-5-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-6-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-7-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-8-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-9-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-10-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-11-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-12-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-13-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-14-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-15-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-16-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-17-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-18-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-19-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-20-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-21-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-22-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-23-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-24-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-25-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-26-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-27-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-28-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-29-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-30-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-10-31-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-1-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-2-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-3-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-4-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-5-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-6-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-7-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-8-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-9-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-10-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-11-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-12-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-13-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-14-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-15-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-16-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-17-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-18-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-19-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-20-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-21-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-22-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-23-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-24-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-25-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-26-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-27-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-28-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-29-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-11-30-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-1-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-2-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-3-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-4-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-5-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-6-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-7-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-8-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-9-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-10-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-11-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-12-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-13-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-14-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-15-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-16-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-17-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-18-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-19-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-20-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-21-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-22-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-23-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-24-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-25-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-26-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-27-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-28-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-29-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-30-1.html', cookiesold)
parse_all_date_page('http://www.3ajiepai.com/archive-2017-12-31-1.html', cookiesold)
# '''

# down_pagefile_thread('http://www.3ajiepai.com/thread-200881-1-1.html', cookiesold, '2018', thread_num=5)
