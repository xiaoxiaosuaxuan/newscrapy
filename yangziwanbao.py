# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "yangziwanbao"
    newspapers = "扬子晚报"
    allowed_domains = ['epaper.yzwb.net']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://epaper.yzwb.net/pc/layout/{date}/node_A01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('layout/\d+/\d+/node_A\w+.html'))),
        Rule(LinkExtractor(allow=('con/\d+/\d+/content_\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath('//div[@class="newsdetatit"]//text()').extract()
            # title = response.xpath("//div[@class='intro']").xpath('string(.)').get()
            # title = title1 + ' ' + title2
            content = response.xpath('//div[@class="newsdetatext"]//text()').extract()
            url = response.url
            date = re.search("con/(\d+/\d+)/", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='newsdetatext']//img/@src").getall()
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