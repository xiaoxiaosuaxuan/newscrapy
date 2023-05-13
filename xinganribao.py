# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "xingandaily"
    newspapers = "兴安日报"
    allowed_domains = ['paper.xingandaily.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y/%m/%d")
        template = "http://paper.xingandaily.cn:81/epaper/xarb/{date}/A01/13871415.shtml"
        for d in dates:
            yield FormRequest(template.format(date=d))

    rules = (
        Rule(LinkExtractor(allow=('xarb/\d+/\d+/\d+/\w+.shtml'))),
        Rule(LinkExtractor(allow=('xarb/\d+/\d+/\d+/\w+/sroty/\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//p[@class='articleTitle']").xpath("string(.)").get()
            # title2 = response.xpath("//div[@class='articleContent']").xpath("string(.)").get()
            # title = title1 + ' ' + title2
            content = response.xpath("//div[@class='articleContent']").xpath('string(.)').get()
            url = response.url
            date = re.search('xarb/(\d+/\d+/\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//p[@align='center']//img/@src").getall()
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