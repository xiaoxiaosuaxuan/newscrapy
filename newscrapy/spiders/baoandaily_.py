# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "baoandaily"
    newspapers = "宝安日报"
    allowed_domains = ['barb.sznews.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://barb.sznews.com/PC/layout/{date}/node_A01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://barb.sznews.com/PC/layout/202208/19/node_A01.html
    rules = (
        Rule(LinkExtractor(allow=('layout/\d+/\d+/node_A\w+.html'))),
        Rule(LinkExtractor(allow=('content/\d+/\d+/content_\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='newsdetatit']").xpath('string(.)').get(all)

            content = response.xpath("//founder-content").xpath('string(.)').get()
            url = response.url
            date = re.search("content/(\d+/\d+)/", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='newsdetatext']/img/@src").getall()
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
