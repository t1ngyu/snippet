#!/usr/bin/python3
# encoding=utf-8
import os
import re
import requests
import click
import mkepub
import json
from lxml import etree

'''
add encoding='utf-8' to _write() of mkepub
def _write(self, template, path, **data):
    with open(str(self.path / path), 'w', encoding='utf-8') as file:
        file.write(env.get_template(template).render(**data))
'''


class NovelSpider:

    def __init__(self, settings):
        self.name = settings['name']
        self.site = settings['site']
        self.next_url = settings['begin_url']
        self.chapter_xpath = settings['chapter_xpath']
        self.chapter_re = settings['chapter_re']
        self.body_xpath = settings['body_xpath']
        self.next_xpath = settings['next_xpath']
        self.data_file = f'{self.name}-data.json'
        self.manifest_file = f'{self.name}-manifest.json'
        self.output_file = f'{self.name}-novel.epub'

    def clear(self):
        for file in [self.data_file, self.manifest_file, self.output_file]:
            if os.path.exists(file):
                os.remove(file)

    def load_manifest(self):
        if os.path.exists(self.manifest_file):
            with open(self.manifest_file, 'r', encoding='utf8') as file:
                obj = json.load(file)
                self.site = obj['site']
                self.next_url = obj['next_url']

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
            url = f'{self.site}{self.next_url}'
            print(url)
            resp = requests.get(url)
            chapter, part, part_count, chapter_title, body, next_url = self.parse(resp.content)
            print(f'{chapter} - {part}/{part_count} {chapter_title}')
            obj = {
                'chapter': chapter,
                'part': part,
                'part_count': part_count,
                'chapter_title': chapter_title,
                'url': self.next_url,
                'next_url': next_url,
                'body': body,
            }
            # 保存文章数据
            json.dump(obj, output)
            output.write('\n')

            # 保存抓取进度
            self.next_url = next_url
            obj = {
                'site': self.site,
                'next_url': self.next_url,
                'chapter': chapter,
                'part': part,
                'part_count': part_count,
            }
            self.save_manifest(obj)

    def parse(self, content):
        ''' 解析文章 '''
        tree = etree.HTML(content)
        # 解析章节信息
        _chapter = tree.xpath(self.chapter_xpath)[0]
        for patt in self.chapter_re:
            m = re.search(patt, _chapter)
            if m:
                break
        if m:
            d = m.groupdict()
            chapter_title = d.get('chapter_title', '')
            chapter = int(d.get('chapter', 0))
            part = int(d.get('part', 0))
            part_count = int(d.get('part_count', 0))
        else:
            print(_chapter)

        # 解析内容
        lines = tree.xpath(self.body_xpath)
        body = '\n'.join(x.replace('\xa0\xa0\xa0\xa0', '  ') for x in lines)
        body = self.purge_article(body)

        # 解析下一页url
        next_url = tree.xpath(self.next_xpath)[0]
        return chapter, part, part_count, chapter_title, body, next_url

    def purge_article(self, text):
        text = text.replace('\xa0', '')
        text = text.replace('&', '')
        return text

    def save(self, begin=0, end=9999999):

            
        with open(self.data_file, 'r', encoding='utf8') as file:
            lines = file.readlines()

        book = mkepub.Book(title='article')
        for line in lines:
            obj = json.loads(line)
            if obj['chapter'] < begin:
                continue
            elif obj['chapter'] > end:
                break
            if obj['part_count'] != 0:
                title = f"第{obj['chapter']}章/第{obj['part']}/{obj['part_count']}页 {obj['chapter_title']}"
            else:
                title = f"第{obj['chapter']}章 {obj['chapter_title']}"
            print(title)
            body = obj['body']
            if not body.startswith('第'):
                body = title + '\n' + body
            book.add_page(title=title, content=body)
        
        output_file = f'{self.name}-book.epub'
        if os.path.exists(output_file):
            os.remove(output_file)
        book.save(output_file)


article_settings = {
    'name': 'chongsheng',
    'site': 'https://m.xs386.com',
    'begin_url': '/14699/6716903.html',
    'chapter_xpath': '//div[@id="nr_title"]/text()',
    'chapter_re': [
        '(?P<chapter>\d+)\.\s*(?P<chapter_title>.*)\(第(?P<part>\d+)/(?P<part_count>\d+)页\)',
        '第(?P<chapter>\d+)章\s*(?P<chapter_title>.+)\(第(?P<part>\d+)/(?P<part_count>\d+)页\)',
        '(?P<chapter>\d+)\.\s*(?P<chapter_title>.+)',
        '第(?P<chapter>\d+)章\s*(?P<chapter_title>.+)',
    ],
    'body_xpath': '//div[@id="nr1"]/text()',
    'next_xpath':  '//a[@id="pb_next"]/@href',
}

nx_settings = {
    'name': 'nx',
    'site': 'https://m.xs386.com',
    'begin_url': '/6661/26067580.html',
    'chapter_xpath': '//div[@id="nr_title"]/text()',
    'chapter_re': [
        '第(?P<chapter>\d+)章\(第(?P<part>\d+)/(?P<part_count>\d+)页\)',
    ],
    'body_xpath': '//div[@id="nr1"]/text()',
    'next_xpath':  '//a[@id="pb_next"]/@href',
}

@click.group()
def cli():
    pass

@cli.command()
def clear():
    spider = NovelSpider(nx_settings)
    spider.clear()

@cli.command()
def scrapy():
    spider = NovelSpider(nx_settings)
    spider.scrapy()

@cli.command()
def make_epub():
    spider = NovelSpider(nx_settings)
    spider.save()

if __name__ == '__main__':
    cli()