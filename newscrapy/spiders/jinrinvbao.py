# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "jinrinvbao"
    newspapers = "今日女报"
    allowed_domains = ['jrnb.fengone.com']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m-%d")
        template = "http://jrnb.fengone.com/new/Html/{date}/Qpaper.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://jrnb.fengone.com/new/Html/2022-12-15/Qpaper.html
#http://jrnb.fengone.com/new/Html/2022-12-15/Qpaper_11593.html
#http://jrnb.fengone.com/new/Html/2022-12-15/22392.html
    rules = (
        Rule(LinkExtractor(allow=('Qpaper'))),
        Rule(LinkExtractor(allow=('Qpaper_\w+'))),
        Rule(LinkExtractor(allow=('\w+')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//td[@class='title']").xpath("string(.)").get()
            content = response.xpath("//div[@id='content']").xpath("string(.)").get()
            url = response.url
            date = re.search('Html/(\d+-\d+-\d+)', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@id='content']//img/@src").getall()
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
