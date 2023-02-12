# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "qdwb"
    newspapers = "青岛晚报"
    allowed_domains = ['epaper.qingdaonews.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "https://epaper.qingdaonews.com/html/qdwb/{date}/index.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('html/qdwb/\d+/index.html'))),
        Rule(LinkExtractor(allow=('html/qdwb/\d+/qdwb0\d.html'))),
        Rule(LinkExtractor(allow=('html/qdwb/\d+/qdwb\d+.html')),callback='parse_item')
    )

    def parse_item(self, response):
        try:
            title = response.xpath(".//table[@id='Table17']//td[@height='40']").xpath("string(.)").get()
            content = response.xpath(".//div[@style='text-align:left']").xpath("string(.)").get()
            imgs = response.xpath(".//div[align='center']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            url = response.url
            date = re.search('qdwb/(\d+)/qdwb', url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
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