# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "dingzhoudaily"
    newspapers = "定州日报"
    allowed_domains = ['szb.dingzhoudaily.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y/%m/%d")
        template = "http://szb.dingzhoudaily.com/epaper/dzrb/html/{date}/02/default.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.dingzhoudaily.com/epaper/dzrb/html/2022/08/18/03/default.htm
#http://szb.dingzhoudaily.com/epaper/dzrb/html/2022/08/18/03/03_40.htm
    rules = (
        Rule(LinkExtractor(allow=('html/\d+/\d+/\d+/\d+/default.htm'))),
        Rule(LinkExtractor(allow=('html/\d+/\d+/\d+/\d+/\d+_\d+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//*[@class='content_title']").xpath('string(.)').get()
            # author=response.xpath("//*[@class='others']").xpath('string(.)').get()
            content = response.xpath("//*[@id='pgcontent']").xpath('string(.)').get()
            url = response.url
            date = re.search("html/(\d+/\d+/\d+)/", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//img[@id='_picsrc']").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html = response.text
        except Exception as e:
            return
#       
        item = NewscrapyItem()
        item['title'] = title
        # item['author'] = author
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = response.url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item
