# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "enshidaily"
    newspapers = "恩施日报"
    allowed_domains = ['szb.enshi.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "https://szb.enshi.cn/esrb/column/{date}/node_A01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#https://szb.enshi.cn/esrb/column/202212/17/node_A01.html
#https://szb.enshi.cn/esrb/content/202212/17/content_105330.html
    rules = (
        Rule(LinkExtractor(allow=('column/\d+/\d+/\w+.html'))),
        Rule(LinkExtractor(allow=('content/\d+/\d+/\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='PreTitle']").xpath('string(.)').get()
            title2 = response.xpath("//*[@id='Title']").xpath('string(.)').get()
            title3 = response.xpath("//*[@id='SubTitle']").xpath('string(.)').get()
            title = title1 + ' ' + title2+' '+title3
            content = response.xpath("//founder-content").xpath('string(.)').get()
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
