# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "chongqingdaily"
    newspapers = "重庆日报"
    allowed_domains = ['epaper.cqrb.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "https://epaper.cqrb.cn/cqrb/{date}/001/node.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('cqrb/\d+-\d+/\d+/\w+/node.htm'))),
        Rule(LinkExtractor(allow=('cqrb/\d+-\d+/\d+/\w+/content_rb_\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//tr[@valign='top']//strong").xpath("string(.)").get()
            content = response.xpath("//div[@id='ozoom']").xpath("string(.)").get()
            url = response.url
            date = re.search("cqrb/(\d+-\d+/\d+)/", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//td[@align='center']//img/@src").getall()
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