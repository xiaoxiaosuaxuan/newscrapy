# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "sichuanfazhibao"
    newspapers = "四川法制报"
    allowed_domains = ['dzb.scfzbs.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "https://dzb.scfzbs.com/shtml/scfzb/{date}/index.shtml"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('scfzb/\d+/index.shtml'))),
        Rule(LinkExtractor(allow=('scfzb/\d+/\d+.shtml')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            pretitle = response.xpath("//div[@class='f-14']").xpath("string(.)").get()
            title0 = response.xpath("//div[@class='f-20']").xpath("string(.)").get()
            title = pretitle + ' ' + title0
            content = response.xpath("//div[@class='f-14 height-25']").xpath("string(.)").get()
            url = response.url
            date = re.search("scfzb/(\d+)/\d+.shtml", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            imgs = response.xpath("//div[@class='f-14 height-25']//img/@src").getall()
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
