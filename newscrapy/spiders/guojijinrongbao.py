# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "guojijinrongbao"
    newspapers = "国际金融报"
    allowed_domains = ['paper.people.com.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://paper.people.com.cn/gjjrb/html/{date}/node_645.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('node.*\.htm'), restrict_xpaths="//div[@class='swiper-box']")),
       Rule(LinkExtractor(allow=('content.*\.htm'), restrict_xpaths="//div[@class='news']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            url = response.url
            html  =response.text
            response = response.xpath("//div[@class='article']")
            title = response.xpath("//h1").xpath("string(.)").get()
            content = response.xpath("//div[@id='ozoom']//p").xpath('string(.)').getall()
            content = "".join(content)
            date = re.search('html/(\d{4}-\d{2}/\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//table[@class='pci_c']//img/@src").getall()
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
