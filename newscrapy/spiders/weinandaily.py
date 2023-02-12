# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "weinandaily"
    newspapers = "渭南日报"
    allowed_domains = ['szb.jsjnews.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://szb.jsjnews.cn/wnrb/{date}/html/index.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('index\.htm'), restrict_xpaths="//*[@class='bmml_con']")),
       Rule(LinkExtractor(allow=('page.*\.htm'), restrict_xpaths="//*[@class='bmml_con']")),
       Rule(LinkExtractor(allow=('content.*\.htm')), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@class='bmnr_con_yinti']").xpath("string(.)").get()
            title2 = response.xpath("//*[@class='bmnr_con_biaoti']").xpath("string(.)").get()
            if not title1:
                title1 = ""
            if not title2:
                title2 = ""
            title = title1 + ' ' + title2
            content = response.xpath("//*[@id='zoom']").xpath('string(.)').get()
            url = response.url
            date = re.search('wnrb/(\d{8})/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            imgs = response.xpath("//*[@id='zoom']//img/@src").getall()
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
