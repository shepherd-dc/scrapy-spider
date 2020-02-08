import MySQLdb
import requests
from scrapy import Selector

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="article_spider", charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    #爬取西拉代理的免费ip代理
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"}
    for i in range(10):
        re = requests.get("http://www.xiladaili.com/gaoni/{0}/".format(i+1), headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.css("table tr")

        for tr in all_trs[1:]:
            all_tds = tr.css("td")
            # ip = all_tds[0].css("td::text").extract_first()
            # port = all_tds[1].css("td::text").extract_first()
            ip_port = all_tds[0].css("td::text").extract_first()
            ip = ip_port.split(':')[0]
            port = ip_port.split(':')[1]
            address = all_tds[3].css("td::text").extract_first()
            proxy_type = all_tds[1].css("td::text").extract_first()
            speed = all_tds[4].css("td::text").extract_first()
            verify_time = all_tds[6].css("td::text").extract_first()

            insert_sql = '''
                insert into proxy_ips(ip, port, address, proxy_type, speed, connect_time, verify_time)
                values (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE ip=VALUES(ip), port=VALUES(port), speed=VALUES(speed)
            '''
            params = (ip, port, address, proxy_type, speed, '', verify_time)
            print(params)
            cursor.execute(insert_sql, params)
            conn.commit()


class GetIP(object):
    def delete_ip(self, ip):
        #从数据库中删除无效的ip
        delete_sql = """
            delete from proxy_ips where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        #判断ip是否可用
        http_url = "http://icanhazip.com/"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            requests.adapters.DEFAULT_RETRIES = 3
            res = requests.get(url=http_url, timeout=8, proxies={"http": proxy_url})
            proxyIP = res.text.replace('\n', '')
            if (proxyIP == ip):
                print("代理IP:'" + proxyIP + "'有效！")
                return True
            else:
                print("代理IP无效！")
                self.delete_ip(ip)
                return False
        except Exception as e:
            print("代理IP无效：", e)
            self.delete_ip(ip)
            return False

        # http_url = "http://www.baidu.com"
        # proxy_url = "http://{0}:{1}".format(ip, port)
        # try:
        #     proxy_dict = {
        #         "http":proxy_url,
        #     }
        #     response = requests.get(http_url, proxies=proxy_dict)
        # except Exception as e:
        #     print("invalid ip and port:", e)
        #     self.delete_ip(ip)
        #     return False
        # else:
        #     code = response.status_code
        #     if code >= 200 and code < 300:
        #         print("effective ip")
        #         return True
        #     else:
        #         print("invalid ip and port")
        #         self.delete_ip(ip)
        #         return False


    def get_random_ip(self):
        #从数据库中随机获取一个可用的ip
        random_sql = """
            SELECT ip, port FROM proxy_ips
            ORDER BY RAND()
            LIMIT 1
            """
        cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

        judge_res = self.judge_ip(ip, port)
        if judge_res:
            return "http://{0}:{1}".format(ip, port)
        else:
            return self.get_random_ip()



# print (crawl_ips())
if __name__ == "__main__":
    get_ip = GetIP()
    get_ip.get_random_ip()
