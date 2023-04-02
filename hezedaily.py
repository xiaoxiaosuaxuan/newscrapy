# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "hezedaily"
    newspapers = "菏泽日报"
    allowed_domains = ['epaper.hezeribao.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://epaper.hezeribao.com/shtml/hzrb/{date}/vA1.shtml"
        for d in dates:
            yield FormRequest(template.format(date=d))

    rules = (
        Rule(LinkExtractor(allow=('shtml/hzrb/\d+/vA\w+.shtml'))),
        Rule(LinkExtractor(allow=('shtml/hzrb/\d+/\w+.shtml')), callback='parse_item')
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='d_t_b']").xpath("string(.)").get()
            content = response.xpath("//div[@class='para']").xpath("string(.)").getall()
            # imgs = body.xpath(".//img/@src").getall()
            imgs = response.xpath("//div[@id='article_img_marquee']//img/@src").getall()
            url = response.url
            date = re.search('hzrb/(\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
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