# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "henandaily"
    newspapers = "河南日报"
    allowed_domains = ['hnrbpaper.dahe.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://hnrbpaper.dahe.cn/html/{date}/node_1.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://hnrbpaper.dahe.cn/html/2022-11/09/node_1.htm
#http://hnrbpaper.dahe.cn/html/2022-11/09/content_603581.htm
    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node\w+.htm'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@id='art_title']").xpath("string(.)").get()
            content = response.xpath("//div[@class='con']").xpath("string(.)").get()
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='pic']//img/@src").getall()
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
