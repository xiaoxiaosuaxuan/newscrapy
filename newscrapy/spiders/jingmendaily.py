# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "jingmendaily"
    newspapers = "荆门日报"
    allowed_domains = ['paper.jmnews.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://paper.jmnews.cn/jmrb/html/{date}/node_3.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://paper.jmnews.cn/jmrb/html/2022-08/19/node_3.htm
#http://paper.jmnews.cn/jmrb/html/2022-08/19/content_558809.htm
    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node\w+'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content\w+')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@class='zh_news']/h3").xpath("string(.)").get()
            title2 = response.xpath("//div[@class='zh_news']/h1").xpath("string(.)").get()
            title3 = response.xpath("//div[@class='zh_news']/h2").xpath("string(.)").get()
            title=title1+title2+title3
            content = response.xpath("//div[@id='ozoom']").xpath("string(.)").get()
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='zh_news_img']//img/@src").getall()
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
