# -*- coding: utf-8 -*-
from subprocess import call
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "weifangdaily"
    newspapers = "潍坊日报"
    allowed_domains = ['wfrb.wfnews.com.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://wfrb.wfnews.com.cn/content/{date}/Page01JQ.htm"
        for d in dates:
            yield FormRequest(template.format(date=d))

    rules = (
        Rule(LinkExtractor(allow=('\d+/Page01JQ.htm'))),
        Rule(LinkExtractor(allow=('\d+/Articel\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@id='title']").xpath("string(.)").get()
            content = response.xpath("//span[@class='font06']").xpath("string(.)").get()
            url = response.url
            date = re.search("content/(\d+)/Articel", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            imgs = response.xpath("//a[@target='_blank']/img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html = response.text
        except Exception as e:
            print(e)
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