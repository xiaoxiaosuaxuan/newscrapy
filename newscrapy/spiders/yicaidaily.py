# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "yicaidaily"
    newspapers = "第一财经日报"
    allowed_domains = ['www.yicai.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "https://www.yicai.com/epaper/pc/{date}/node_A01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('node.*\.html'), restrict_xpaths="//div[@class='Therestlist']")),
       Rule(LinkExtractor(allow=('content.*\.html'), restrict_xpaths="//div[@class='newslist']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            html  =response.text
            url = response.url
            title = response.xpath("//div[@class='newsdetatit']//h3").xpath("string(.)").get()
            content = response.xpath("//founder-content").xpath('string(.)').get()
            date = re.search('pc/(\d{6}/\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='newsdetatext']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
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