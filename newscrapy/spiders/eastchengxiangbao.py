# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "eastchengxiangbao"
    newspapers = "东方城乡报"
    allowed_domains = ['www.dfcxb.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://www.dfcxb.com/html/{date}/node_1.htm?v=1"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('node.*\.htm'), restrict_xpaths="//table/tbody/tr")),
       Rule(LinkExtractor(allow=('content.*\.htm'), restrict_xpaths="//div[@id='main-ed-articlenav-list']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            title = response.xpath("//founder-title").xpath("string(.)").get()
            content = response.xpath("//founder-content").xpath('string(.)').get()
            url = response.url
            date = re.search('html/(\d{4}-\d{2}/\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//table[@id='newspic']//img/@src").getall()
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
