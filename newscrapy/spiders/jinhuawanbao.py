# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "jinhuawanbao"
    newspapers = "金华晚报"
    allowed_domains = ['epaper.jhnews.com.cn']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "https://epaper.jhnews.com.cn/jrwb/jhwbpaper/pc/layout/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#https://epaper.jhnews.com.cn/jrwb/jhwbpaper/pc/layout/202208/29/node_01.html
#https://epaper.jhnews.com.cn/jrwb/jhwbpaper/pc/con/202208/29/content_360041.html
    rules = (
        Rule(LinkExtractor(allow=('layout/\d+/\d+/node_\w+.html'))),
        Rule(LinkExtractor(allow=('con/\d+/\d+/content_\w+.html')),callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='main-article-alltitle']").xpath("string(.)").get()
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search('con/(\d+/\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='attachment']//img/@src").getall()
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
