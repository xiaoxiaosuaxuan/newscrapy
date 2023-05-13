# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "binzhoudaily"
    newspapers = "滨州日报"
    allowed_domains = ['epaper.bzrb.net']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://epaper.bzrb.net/bzrb/{date}/html/page_01.htm"
        for d in dates:
            yield FormRequest(template.format(date=d))

    rules = (
        Rule(LinkExtractor(allow=('bzrb/\d+/html/page_\w+.htm'))),
        Rule(LinkExtractor(allow=('bzrb/\d+/html/content_\w+.htm')), callback='parse_item')
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='bmnr_con_biaoti']").xpath("string(.)").get()
            content = response.xpath("//div[@id='zoom']").xpath("string(.)").getall()
            # imgs = body.xpath(".//img/@src").getall()
            imgs = response.xpath("//div[@id='zoom']//img/@src").getall()
            url = response.url
            date = re.search('bzrb/(\d+)/html', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            html = response.text
        except Exception as e:
            return

        item = NewscrapyItem()
        item['title'] = title
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = response.url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item