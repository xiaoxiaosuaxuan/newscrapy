# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "baodingdaily"
    newspapers = "保定日报"
    allowed_domains = ['epaper.bdall.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://epaper.bdall.com/rbpaper/pc/layout/{date}/node_a1.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://epaper.bdall.com/rbpaper/pc/layout/202208/20/node_a1.html
#../../../content/202208/20/content_107440.html
    rules = (
        Rule(LinkExtractor(allow=('layout/\d+/\d+/node_a\w+.html'))),
        Rule(LinkExtractor(allow=('content/\d+/\d+/content_\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='newsdetatit']").xpath('string(.)').get()
            content = response.xpath("//founder-content").xpath('string(.)').get()
            url = response.url
            date = re.search("content/(\d+/\d+)/", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='pic']//img/@src").getall()
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
