# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "jinanshibao"
    newspapers = "济南时报"
    allowed_domains = ['jnsb.e23.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://jnsb.e23.cn/shtml/jnsb/{date}/vA01.shtml"
        for d in dates:
            yield FormRequest(template.format(date=d))

    rules = (
        Rule(LinkExtractor(allow=('shtml/jnsb/\d+/vA\w+.shtml'))),
        Rule(LinkExtractor(allow=('shtml/jnsb/\d+/\w+.shtml')), callback='parse_item')
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='detail']//h2").xpath("string(.)").get()
            content = response.xpath("//p[@align='left']").xpath("string(.)").getall()
            # imgs = body.xpath(".//img/@src").getall()
            imgs = response.xpath("//div[@class='article']//img/@src").getall()
            url = response.url
            date = re.search('jnsb/(\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
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