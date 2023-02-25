# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "loudiwanbao"
    newspapers = "娄底晚报"
    allowed_domains = ['ldwb.ldnews.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y/%m/%d")
        template = "http://ldwb.ldnews.cn/{date}/index.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://ldwb.ldnews.cn/2022/12/15/index_2.html
#http://ldwb.ldnews.cn/2022/12/15/index.html
#http://ldwb.ldnews.cn/2022/12/15/619637.html
    rules = (
        Rule(LinkExtractor(allow=('\d+/\d+/\d+/index'))),
        Rule(LinkExtractor(allow=('\d+/\d+/\d+/index_\w+'))),
        Rule(LinkExtractor(allow=('\d+/\d+/\d+/\w+')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@class='bd_Right']/h1").xpath("string(.)").get()
            title2 = response.xpath("//div[@class='bd_Right']/span[2]").xpath("string(.)").get()
            title = title1 + ' ' + title2
            content = response.xpath("//div[@id='content']").xpath('string(.)').get()
            url = response.url
            date = re.search('(\d+/\d+/\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@id='content']//img/@src").getall()
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

