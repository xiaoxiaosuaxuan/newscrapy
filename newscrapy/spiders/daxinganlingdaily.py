# -*- coding: utf-8 -*-
from scrapy import FormRequest
import regex as re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "daxinganlingdaily"
    newspapers = "大兴安岭日报"
    allowed_domains = ['paper.dxalrb.org.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://paper.dxalrb.org.cn/dxalrb/pc/layout/{date}/node_A01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://paper.dxalrb.org.cn/dxalrb/pc/layout/202208/25/node_A01.html
#http://paper.dxalrb.org.cn/dxalrb/pc/con/202208/25/content_5594.html
    rules = (
        Rule(LinkExtractor(allow=('layout/\d+/\d+/node_A\w+.html'))),
        Rule(LinkExtractor(allow=('con/\d+/\d+/content_\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='newsdetatit']/h3").xpath('string(.)').get()
            content = response.xpath("//founder-content").xpath('string(.)').get()
            url = response.url
            date = re.search("con/(\d+/\d+)/", url).group(1)
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
