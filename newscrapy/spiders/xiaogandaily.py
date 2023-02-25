# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "xiaogandaily"
    newspapers = "孝感日报"
    # allowed_domains = ['szb.xgrb.cn:9999']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y/%m/%d")
        template = "http://szb.xgrb.cn:9999/epaper/xgrb/html/{date}/01/default.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.xgrb.cn:9999/epaper/xgrb/html/2022/07/04/01/default.htm
#http://szb.xgrb.cn:9999/epaper/xgrb/html/2022/07/04/01/01_64.htm
    rules = (
        Rule(LinkExtractor(allow=('html/\d+/\d+/\d+/\w+/default'))),
        Rule(LinkExtractor(allow=('html/\d+/\d+/\d+/\w+/\w+')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//h5[@class='yinti_title']").xpath("string(.)").get()
            title2 = response.xpath("//h2[@class='content_title']").xpath("string(.)").get()
            title = title1 + ' ' + title2
            content = response.xpath("//div[@id='pgcontent']").xpath('string(.)').get()
            url = response.url
            date = re.search('html/(\d+/\d+/\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//table[@id='pictable4']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html  =response.text
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

