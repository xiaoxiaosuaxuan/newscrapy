# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "wenhuibao"
    newspapers = "文汇报"
    allowed_domains = ['dzb.whb.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m-%d")
        template = "http://dzb.whb.cn/{date}/1/index.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('\d/index\.html'), restrict_xpaths="//*[@id='spaceBox']")),
       Rule(LinkExtractor(allow=("\d/detail.*\.html"), restrict_xpaths="//div[@class='title_box  list']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='news_header']").xpath("string(.)").get()
            content = response.xpath("//*[@id='newsContent']").xpath('string(.)').get()
            url = response.url
            date = re.search('/(\d{4}-\d{2}-\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='img']//img/@src").getall()
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
