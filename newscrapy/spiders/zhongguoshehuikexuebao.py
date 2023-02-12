# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "zhongguoshehuikexuebao"
    newspapers = "中国社会科学报"
    allowed_domains = ['sspress.cssn.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Yn/%my/%d")
        template = "http://sspress.cssn.cn/{date}/d1b/"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('http://sspress.cssn.cn/\d+n/\d+y/\d+/d\d+b/'))),
        Rule(LinkExtractor(allow=('http://sspress.cssn.cn/\d+n/\d+y/\d+/d\d+b/\w+/\w+.shtml')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='xl_title']").xpath("string(.)").get()
            content = response.xpath("//div[@class='allblock']//p").xpath("string(.)").get()
            url = response.url
            date = re.search("cn/(\d+n/\d+y/\d+)/d", url).group(1)
            date = '-'.join([date[0:4], date[6:8], date[10:12]])
            imgs = response.xpath("//p[@align='center']//img/@src").getall()
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
