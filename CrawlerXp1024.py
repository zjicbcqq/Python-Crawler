from Crawler import Crawler
import os


######################################################


cookiesold = {
    '3nvN_7b26_auth': 'fc507Qk76p3hkwdqo8OYYIRm7LfVdlr1uLzZAazcNr5QcfOOMo%2BXaqSRuM9juSeKn7WWR6q87Gg3Yv28OcO9YfpnInw',
    '3nvN_7b26_checkfollow': '1', '3nvN_7b26_lastact': '1518073249%09member.php%09logging',
    '3nvN_7b26_lastcheckfeed': '227970%7C1518073249', '3nvN_7b26_lastvisit': '1518069649',
    '3nvN_7b26_lip': '58.62.52.111%2C1518073057', '3nvN_7b26_pc_size_c': '0', '3nvN_7b26_saltkey': 's5xE5LR2',
    '3nvN_7b26_sid': 'a92CL9', '3nvN_7b26_ulastactivity': '3f446m9k%2F3JqghhOTMXQfJ%2BJ8arjpUFb3F7DHMJ69x4MOPx5IyGa'}


class CrawlerXp1024(Crawler):
    def __init__(self):
        super().__init__()
        return

    def on_gen_all_page(self, *args):
        """
        自定义页面链接生成规则，加入列表
        :param url: 主链接
        :param li: list 作为参数
        :rtype:
        :return:
        """
        url = self.url[0:-1]

        for i in range(args[0], args[1] + 1):
            new_url = url + '%d' % i
            print(new_url)
            d = {"url": new_url}
            Crawler.lock.acquire()
            self.append_page_info_list(d)
            Crawler.lock.release()

        return

    def on_parse_page(self, soup):
        """
        自定义解析规则，解析页面找到每个帖子所在区块
        :param soup: BeautifulSoup
        :rtype:
        :return:
        """
        childs = soup.find_all('tr', class_="tr3 t_one")
        return childs

    def on_parse_page_child(self, child):
        """
        自定义解析规则, 从页面解析帖子链接信息
        :param child:
        :param info:
        :param index:
        :rtype:
        :return:
        """
        td = child.td

        td = child.td
        td = td.next_sibling
        if td.h3 is None:
            return None
        href = str(self.url_host) + 'pw/' + td.h3.a['href']

        name = td.h3.a.string[8:]

        td = td.next_sibling
        td = td.next_sibling
        td = td.next_sibling
        td = td.next_sibling
        td = td.next_sibling
        td = td.next_sibling
        date_time = td.string
        date = date_time[1:11]

        # print(href, name, date)

        new_info = {'url': href, 'name': name, 'date': date}

        return new_info

    def on_parse_post(self, soup):
        """
        自定义解析规则，解析帖子找到每个下载区块
        :param soup: BeautifulSoup
        :rtype:
        :return:
        """
        childs = soup.find_all('img', onload="if(this.width>'1024')this.width='1024';")

        return childs

    def on_parse_post_child(self, child, info, index):
        """
        自定义解析规则, 从帖子解析下载链接信息
        :param child:
        :param info:
        :param index:
        :rtype:
        :return:
        """
        url = child['src']
        index_s = '%03d' % index

        new_info = {'url': url, 'name': info['name'], 'date': info['date'], 'index': index_s}

        return new_info

    def on_down_file(self, info):
        """
        下载预处理接口,从info提取数据返回链接和文件名
        :param info: 下载文件相关信息
        :rtype:
        :return:
        """
        url = info['url']
        if url == '':
            return None
        name = os.path.basename(url)
        # 问号不能做文件名，需要替换
        name = name.replace('?', '9')
        # 按格式重组文件名
        name = info['date'] + '_' + info['name'] + '_' + info['index'] + '_' + name

        # print("文件名[%s]" % name)
        # return None

        # 返回 链接 和 文件名
        return {'url': url, 'name': name}


c = CrawlerXp1024()
# c.cookies = cookiesold
c.set_url('http://s2.lulujjs.net/pw/thread.php?fid=49&page=2')
c.save_path = 'img/'
# c.encoding = 'GBK'
c.max_thread_num = 10
c.gen_all_page(2, 50)
c.deal_down_list()
