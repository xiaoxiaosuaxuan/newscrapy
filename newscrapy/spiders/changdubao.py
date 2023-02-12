# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "changdubao"
    newspapers = "昌都报"
    allowed_domains = ['sz.cdbao.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://sz.cdbao.cn/cdb/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('node.*\.html'), restrict_xpaths="//div[@class='nav-list']")),
       Rule(LinkExtractor(allow=('content.*\.html'), restrict_xpaths="//div[@class='news-list']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            title = response.xpath("//*[@id='Title']").xpath("string(.)").get()
            content = response.xpath("//*[@id='ozoom']").xpath('string(.)').get()
            url = response.url
            date = re.search('cdb/(\d{6}/\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='attachment']//img/@src").getall()
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

