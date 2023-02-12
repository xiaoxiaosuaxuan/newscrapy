# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "changjidaily"
    newspapers = "昌吉日报"
    allowed_domains = ['218.31.200.249']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://218.31.200.249:92/pc/layout/{date}/node_01B.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('node.*\.html'), restrict_xpaths="//div[@class='nav-list']")),
       Rule(LinkExtractor(allow=('content.*\.html'), restrict_xpaths="//div[@class='news-list']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            title = response.xpath("//*[@class='totalTitle']").xpath("string(.)").get()
            content1 = response.xpath("//div[@class='attachment']//*[@class='img_text']").xpath("string(.)").get()
            content2 = response.xpath("//founder-content").xpath('string(.)').get()
            content = content1 + content2
            url = response.url
            date = re.search('cont/(\d{6}/\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='attachment']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html  =response.text
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

