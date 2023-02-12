# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "shannanbao"
    newspapers = "山南报"
    allowed_domains = ['epaper.xzsnw.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://epaper.xzsnw.com/snbhw/html/{date}/node_7.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('node.*\.htm'), restrict_xpaths="//a[@id='pageLink']")),
       Rule(LinkExtractor(allow=('content.*\.htm')), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            html = response.text 
            url = response.url
            response = response.xpath("//div[@style='height:800px; overflow-y:scroll; width:100%;']")
            title = response.xpath("//td[@align='center' and @class='font01']").xpath("string(.)").get()
            content = response.xpath("//founder-content").xpath('string(.)').get()
            date = re.search('html/(\d{4}-\d{2}/\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = []
        except Exception as e:
            return
        
        item = NewscrapyItem()
        item['title'] = title
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item
