# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "chongqingzhengxiebao"
    newspapers = "重庆政协报"
    allowed_domains = ['cqzxb.itlic.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "https://cqzxb.itlic.com/content/{date}/01"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('content/\d+-\d+/\d+/\d{2}'))),
        Rule(LinkExtractor(allow=('content/\d+-\d+/\d+/\d+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@style='font-size: 1.7em;font-family:'Microsoft YaHei','微软雅黑','黑体';line-height: 2.3em;text-align: center;color: #201f1f;']").xpath("string(.)").get()
            content = response.xpath("//div[@id='newspapercontent']").xpath("string(.)").get()
            url = response.url
            date = re.search("content/(\d+-\d+/\d+)/\d{6}.html", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@id='newspapercontent']//img/@src").getall()
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
