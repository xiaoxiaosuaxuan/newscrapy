# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "tulufandaily"
    newspapers = "吐鲁番日报"
    allowed_domains = ['epaper.tlfw.net']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://epaper.tlfw.net/tlf/content/{date}/Page01BC.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('Page.*\.htm'), restrict_xpaths="//div[@class='gebanlist_2']")),
       Rule(LinkExtractor(allow=('Articel.*\.htm'), restrict_xpaths="//div[@class='newslist']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            url = response.url
            html = response.text
            response = response.xpath("//div[@class='neirong']")
            title1 = response.xpath("//h3").xpath("string(.)").get()
            title2 = response.xpath("//h2").xpath("string(.)").get()
            if not title1:
                title1 = ""
            if not title2:
                title2 = ""
            title = title1 + ' ' + title2
            content = response.xpath("//*[@id='contenttext']").xpath('string(.)').get()
            date = re.search('content/(\d{8})/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            imgs = response.xpath("//div[@class='imagelist']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
        except Exception as e:
            return
        
        item = NewscrapyItem()
        item['title'] = title
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item
