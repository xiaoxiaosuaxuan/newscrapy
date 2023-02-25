# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "puyangdaily"
    newspapers = "濮阳日报"
    allowed_domains = ['pyrb.pyxww.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://pyrb.pyxww.com/{date}/l01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://pyrb.pyxww.com/202208/16/l01.html
#http://pyrb.pyxww.com/content/202208/16/c103300.html
    rules = (
        Rule(LinkExtractor(allow=('\d+/\d+/l\w+.html'))),
        Rule(LinkExtractor(allow=('content/\d+/\d+/c\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//p[@class='introtitle text-center']").xpath('string(.)').get(all)
            title2 = response.xpath("//h2[@class='art-title text-center']").xpath('string(.)').get()
            title3 = response.xpath("//p[@class='subtitle text-center']").xpath('string(.)').get()
            title = title1 + ' ' + title2+ ' ' + title3
            content = response.xpath("//founder-content").xpath('string(.)').get(all)
            url = response.url
            date = re.search("content/(\d+/\d+)/", url).group(1)
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
