#!/usr/bin/python3
# coding=utf-8


from urllib import request
from urllib import response
import re
import base64

class Oray:
    '''
    http://open.oray.com/wiki/doku.php?id=%E6%96%87%E6%A1%A3:%E8%8A%B1%E7%94%9F%E5%A3%B3:http%E5%8D%8F%E8%AE%AE%E8%AF%B4%E6%98%8E
    '''

    def __init__(self, username, password, domain):
        self.URL_CHECK_IP = 'http://ddns.oray.com/checkip'
        self.URL_UPDATE_IP = 'http://ddns.oray.com/ph/update'
        self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'

        self.username = username
        self.password = password
        self.domain = domain
        if not self.domain:
            self.domain = ''

        opener = request.build_opener(request.BaseHandler())
        opener.addheaders = [('Accept', '*/*'),
                            ('User-Agent', self.USER_AGENT),
                            ('Accept-Language', 'zh-CN,zh;q=0.8')]
        request.install_opener(opener)

    def checkip(self):
        resp = request.urlopen(self.URL_CHECK_IP)
        data = resp.read().decode('utf-8')
        patt = re.compile('Address: ([\d.]+)')
        match = patt.search(data)
        if match:
            return match.group(1)


    def update(self, ip=None):
        url = '{0}?hostname={1}&myip={2}'.format(self.URL_UPDATE_IP, self.domain, ip)
        req = request.Request(url)
        authorization = base64.b64encode('{0}:{1}'.format(self.username, self.password).encode('utf-8'))
        authorization = authorization.decode('ascii')
        req.add_header('Authorization', 'Basic {0}'.format(authorization))
        resp = request.urlopen(req)
        if resp.code == 200:
            data = resp.read()
            if 'good' or 'nochg' or 'abuse' in data:
                return True


if __name__ == '__main__':
    import time
    import logging

    logging.basicConfig(filename='oray.log', format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.INFO)

    username = 'yourusername'
    password = 'yourpassword'
    domain = 'yourid.oicp.net'

    previous_ip = None
    current_ip = None

    oray = Oray(username, password, domain)

    while True:
        try:
            current_ip = oray.checkip()
            logging.info(current_ip)
            if current_ip:  #and current_ip != previous_ip:
                if oray.update(current_ip):
                    logging.info("Update ip successfully.")
                    previous_ip = current_ip
                else:
                    logging.warning("Update ip failed!")
        except Exception as e:
            logging.error(e)
            pass
        time.sleep(60 * 10)

