# encoding=utf-8
import os
import re
import requests
import mkepub
import json
from lxml import etree


class ArticleSpider:

    site = 'https://m.xs386.com'
    begin_url = '/6661/26067580.html'
    data_file = 'data.json'
    manifest_file = 'manifest.json'

    def __init__(self):
        self.url = self.begin_url

    def clean(self):
        for file in [self.data_file, self.manifest_file, self.output_file]:
            if os.path.exists(file):
                os.remove(file)

    def load_manifest(self):
        if os.path.exists(self.manifest_file):
            with open(self.manifest_file, 'r', encoding='utf8') as file:
                obj = json.load(file)
                self.site = obj['site']
                self.url = obj['next_url']

    def save_manifest(self, obj):
        with open(self.manifest_file, 'w', encoding='utf8') as file:
            json.dump(obj, file)

    def scrapy(self):
        ''' 抓取 '''
        # 加载抓取进度
        self.load_manifest()

        # 开始抓取
        output = open(self.data_file, 'a', encoding='utf8')
        while True:
            url = f'{self.site}{self.url}'
            print(url)
            resp = requests.get(url)
            chapter, section, total, body, next_url = self.parse(resp.content)
            print(f'{chapter} - {section}/{total}')
            obj = {
                'chapter': chapter,
                'section': section,
                'total': total,
                'url': self.url,
                'next_url': next_url,
                'body': body,
            }
            # 保存文章数据
            json.dump(obj, output)
            output.write('\n')

            # 保存抓取进度
            self.url = next_url
            obj = {
                'site': self.site,
                'next_url': self.url,
                'chapter': chapter,
                'part': section,
                'total': total,
            }
            self.save_manifest(obj)

    def parse(self, content):
        ''' 解析文章 '''
        tree = etree.HTML(content)
        text = tree.xpath('//div[@id="nr_title"]/text()')[0]
        m = re.search('第(\d+)章\(第(\d+)/(\d+)页\)', text)
        if m:
            chapter, section, total = m.groups()
            chapter = int(chapter)
            section = int(section)
            total = int(total)
        else:
            print(text)
        next_url = tree.xpath('//a[@id="pb_next"]/@href')[0]
        lines = tree.xpath('//div[@id="nr1"]/text()')
        body = '\n'.join(x.replace('\xa0\xa0\xa0\xa0', '  ') for x in lines)
        body = self.purge_article(body)
        return chapter, section, total, body, next_url

    def purge_article(self, text):
        text = text.replace('\xa0', '')
        text = text.replace('&', '')
        return text

    def save(self, filename='note.epub', begin=0, end=9999999):
        with open(self.data_file, 'r', encoding='utf8') as file:
            lines = file.readlines()

        book = mkepub.Book(title='article')
        for line in lines:
            obj = json.loads(line)
            if obj['chapter'] < begin:
                continue
            elif obj['chapter'] > end:
                break
            title = f"第{obj['chapter']}章/第{obj['part']}/{obj['total']}页"
            print(title)
            body = obj['body']
            if not body.startswith('第'):
                body = title + '\n' + body
            book.add_page(title=title, content=body)
        book.save(filename)

spider = ArticleSpider()
# spider.clean()
# spider.scrapy()
spider.save('note.epub')
# make_epub2()
