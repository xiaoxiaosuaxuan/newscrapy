# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "dongnanearly"
    newspapers = "东南早报"
    allowed_domains = ['szb.qzwb.com']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "https://szb.qzwb.com/dnzb/html/{date}/node_42.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('node_\w+\.htm'))),
        Rule(LinkExtractor(allow=('content_\w+\.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//*[@class='font01']").xpath("string(.)").get()
            content = response.xpath("//founder-content").xpath("string(.)").get(all)
            url = response.url
            date = re.search('html/(\d+-\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='tupian']//img").getall()
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
