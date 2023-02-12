# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "jiefangdaily"
    newspapers = "解放日报"
    allowed_domains = ['www.jfdaily.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m-%d")
        template = "https://www.jfdaily.com/staticsg/res/html/journal/index.html?date={date}&page=01"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
       Rule(LinkExtractor(allow=('html\?date=.*&page=.*'), restrict_xpaths="//div[@class='right-area']")),
       Rule(LinkExtractor(allow=('html\?date=.*&id=.*&page=.*'), restrict_xpaths="//div[@class='middle-area']"), callback="parse_item")
    )
    
    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='con-title']").xpath("string(.)").get()
            content = response.xpath("//div[@class='txt-box']").xpath('string(.)').get()
            url = response.url
            date = re.search('date=/(\d{4}-\d{2}-\d{2})/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='pic-box']//img/@src").getall()
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
