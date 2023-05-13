# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "nongcunyiyaobao"
    newspapers = "农村医药报"
    allowed_domains = ['d.ncyyw.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m-%d")
        template = "http://d.ncyyw.cn/Html/{date}/Qpaper_1511.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('Html/\d+-\d+-\d+/Qpaper_\w+.html'))),
        Rule(LinkExtractor(allow=('Html/\d+-\d+-\d+/\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='xnr5_t1']").xpath("string(.)").get()
            content = response.xpath("//div[@id='content']").xpath("string(.)").get()
            url = response.url
            date = re.search('Html/(\d+-\d+-\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@id='content']//img/@src").getall()
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