# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "yongzhoudaily"
    newspapers = "永州日报"
    # allowed_domains = ['paper.0746news.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m-%d")
        template = "http://paper.0746news.com/Html/{date}/Qpaper.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://paper.0746news.com/Html/2022-08-31/Qpaper.html
#http://paper.0746news.com/Html/2022-08-31/Qpaper_43259.html
#http://paper.0746news.com/Html/2022-08-31/214347.html
    rules = (
        Rule(LinkExtractor(allow=('Html/\d+-\d+-\d+/Qpaper.htm'))),
        Rule(LinkExtractor(allow=('Html/\d+-\d+-\d+/Qpaper_\w+.htm'))),
        Rule(LinkExtractor(allow=('Html/\d+-\d+-\d+/\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@id='yinti']").xpath("string(.)").get()
            title2 = response.xpath("//div[@id='doctitle']").xpath("string(.)").get()
            title3 = response.xpath("//div[@id='subdoctitle']").xpath("string(.)").get()
            title=title1+title2+title3
            content = response.xpath("//div[@id='doccontent']").xpath("string(.)").get()
            url = response.url
            date = re.search("Html/(\d+-\d+-\d+)", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@id='doccontent']//img/@src").getall()
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
