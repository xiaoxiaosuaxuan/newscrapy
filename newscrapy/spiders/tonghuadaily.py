# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "tonghuadaily"
    newspapers = "通化日报"
    allowed_domains = ['www.thrbs.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://www.thrbs.com/Html/szbz/{date}/Index.Html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://www.thrbs.com/Html/szbz/20221216/Index.Html
#http://www.thrbs.com/Html/szbz/20221216/szbzA2.Html
#http://www.thrbs.com/html/szbz/20221216/szbz376112.Html
    rules = (
        Rule(LinkExtractor(allow=('szbz/\d+/Index.Html'))),
        Rule(LinkExtractor(allow=('szbz/\d+/szbzA\w+'))),
        Rule(LinkExtractor(allow=('szbz/\d+/szbz\w+')),callback='parse_item')
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//td[@height='40']").xpath("string(.)").get()
            content = response.xpath("//div[@id='ozoom']").xpath("string(.)").get()
            imgs = response.xpath("//div[@id='copytext']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            url = response.url
            date = re.search('szbz/(\d+)', url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
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
