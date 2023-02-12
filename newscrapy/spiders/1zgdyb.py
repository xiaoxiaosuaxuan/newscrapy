# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "zgdyb"
    newspapers = "中国电影报"
    allowed_domains = ['chinafilmnews.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m-%d")
        template = "http://chinafilmnews.cn/Html/{date}/Qpaper.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('Html/\d+-\d+-\d+/Qpaper_\d+.html'))),
        Rule(LinkExtractor(allow=('Html/\d+-\d+-\d+/Qpaper.html'))),
        Rule(LinkExtractor(allow=('Html/\d+-\d+-\d+/\d+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='title']").xpath("string(.)").get()
            content = response.xpath("//div[@class='content']//p[@style='text-indent: 2em;']").xpath('string(.)').getall()
            url = response.url
            date = re.search('Html/(\d+-\d+-\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='content']//img/@src").getall()
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