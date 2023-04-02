# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "chaozhoudaily"
    newspapers = "潮州日报"
    allowed_domains = ['www.chaozhoudaily.com']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://www.chaozhoudaily.com/czrb/html/{date}/node_2.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://www.chaozhoudaily.com/czrb/html/2022-08/28/content_1910645.htm
#http://www.chaozhoudaily.com/czrb/html/2022-08/28/node_2.htm
    rules = (
        Rule(LinkExtractor(allow=('node_\w+.htm'))),
        Rule(LinkExtractor(allow=('content_\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//td[@class='font02']").xpath('string(.)').get()
            title2 = response.xpath("//td[@class='font01']").xpath('string(.)').get()
            title = title1 + ' ' + title2
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search('html/(\d+-\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//td[@align='center']//img/@src").getall()
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
