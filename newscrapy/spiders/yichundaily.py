# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "yichundaily"
    newspapers = "伊春日报"
    allowed_domains = ['60.11.44.37']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://60.11.44.37/content/{date}/node_19.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://60.11.44.37/content/2023-01/03/node_19.htm
#http://60.11.44.37/content/2023-01/03/content_87264.htm
    rules = (
        Rule(LinkExtractor(allow=('node_\w+\.htm'))),
        Rule(LinkExtractor(allow=('content_\w+\.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//td[@class='font02']").xpath("string(.)").get()
            title2 = response.xpath("//td[@class='font01']").xpath("string(.)").get()
            title=title1+title2
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search('content/(\d+-\d+/\d+)', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//td[@class='font6']//img/@src").getall()
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
