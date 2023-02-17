# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "meirijinjixinwen"
    newspapers = "每日经济新闻"
    allowed_domains = ['epaper.mrjjxw.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://epaper.mrjjxw.com/shtml/mrjjxw/{date}/index.shtml"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('v.*\.shtml'), restrict_xpaths="//div[@class='pageNav']")),
       Rule(LinkExtractor(allow=('\d+\.shtml'), restrict_xpaths="//div[@class='titleNav']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            html  =response.text
            url = response.url
            response = response.xpath("//*[@div='content']")
            title = response.xpath("//h1").xpath("string(.)").get()
            content = response.xpath("//div[@id='content_div']").xpath('string(.)').get()
            date = re.search('mrjjxw/(\d{8})/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            imgs = response.xpath("//div[@id='art']//img/@src").getall()
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
