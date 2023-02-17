# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "xiandaily"
    newspapers = "西安日报"
    allowed_domains = ['epaper.xiancn.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "https://epaper.xiancn.com/newxarb/pc/html/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('node.*\.htm'), restrict_xpaths="//*[@id='bmlistbar']")),
       Rule(LinkExtractor(allow=('content.*\.htm'), restrict_xpaths="//*[@id='main-ed-articlenav-list']"), callback="parse_item", )
    )
    
    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='Title']").xpath("string(.)").get()
            title2 = response.xpath("//*[@id='SubTitle']").xpath("string(.)").get()
            if not title1:
                title1 = ""
            if not title2:
                title2 = ""
            title = title1 + ' ' + title2
            content = response.xpath("//*[@id='content']").xpath('string(.)').get()
            url = response.url
            date = re.search('html/(\d{6}/\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//*[@class='attachment']//img/@src").getall()
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
