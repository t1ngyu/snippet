import os
import sys
from urllib import request


def parse_request(file):
    with open(file, 'r') as f:
        line = f.readline()
        url = line.split(' ')[1]
        headers = {}
        while True:
            line = f.readline()
            if (not line) or (not':' in line):
                break
            fields = line.split(':', 1)
            headers[fields[0]] = fields[1].strip(' \x0d\x0a')
    return {'url': url, 'headers': headers}


def download(req_header, file):
    url = 'http://{}{}'.format(req_header['headers']['Host'], req_header['url'])
    print(url)
    req = request.Request(url, method='GET')
    headers = req_header['headers']
    for k in headers:
        req.add_header(k, headers[k])
    print(req)
    resp = request.urlopen(req)
    if resp and resp.code == 200:
        print('File length: {}'.format(resp.length))
        print('saving...')
        f = open(output_file, 'wb')
        f.write(resp.read())
        f.close()

    print('Done!')
    
if __name__ == '__main__':

    download_dir = r'D:\download'

    if len(sys.argv) == 2:
        request_file = sys.argv[1]
        filename = os.path.basename(request_file)
        filename = filename.rsplit('.', 1)[0]
        output_file = os.path.join(download_dir, '{0}.mp4'.format(filename))
        
        print(output_file)
        
        req = parse_request(request_file)
        download(req, output_file)
    
    