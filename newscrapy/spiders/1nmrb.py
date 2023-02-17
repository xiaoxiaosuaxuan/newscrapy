# -*- coding: utf-8 -*-
from subprocess import call
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "nmrb"
    newspapers = "农民日报"
    allowed_domains = ['szb.farmer.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "https://szb.farmer.com.cn/2022/{date}/{date}_001/{date}_001.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('\d+/\d+/\d+_\d+/\d+_\d+.html'))),
        Rule(LinkExtractor(allow=('\d+/\d+/\d+_\d+/\d+_\d+_\d+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath(".//td[@class='font01']").xpath("string(.)").get()
            title2 = response.xpath(".//td[@class='font02']").xpath("string(.)").get()
            title = title1+title2
            content = response.xpath("//td[@class='font6']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("\d+/(\d+)/\d+_\d+", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            imgs = response.xpath(".//td[@class='font6']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
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