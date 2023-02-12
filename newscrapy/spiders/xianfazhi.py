# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "xianfazhi"
    newspapers = "西安法制报"
    allowed_domains = ['esb.xbfzb.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://esb.xbfzb.com/html/{date}/node_1.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('node.*\.htm'), restrict_xpaths="//*[@id='breakNewsList1']")),
       Rule(LinkExtractor(allow=('content.*\.htm')), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@class='bmnr_con_biaoti']").xpath("string(.)").get()
            title2 = response.xpath("//*[@class='bmnr_con_yinti']").xpath("string(.)").get()
            title = title1 + ' ' + title2
            content = response.xpath("//*[@id='zoom']").xpath('string(.)').get()
            url = response.url
            date = re.search('html/(\d+-\d+/\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='bmnr_con']//img/@src").getall()
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

