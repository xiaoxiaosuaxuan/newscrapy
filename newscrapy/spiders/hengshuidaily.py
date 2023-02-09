# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "hengshuidaily"
    newspapers = "衡水日报"
    allowed_domains = ['www.fzsyun.cn']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://www.fzsyun.cn/hsrb/{date}/node_A1.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://www.fzsyun.cn/hsrb/2022-05/23/node_A1.html
#http://www.fzsyun.cn/hsrb/2022-05/23/content_349930.html
    rules = (
        Rule(LinkExtractor(allow=('node\w+\.htm'))),
        Rule(LinkExtractor(allow=('content\w+\.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='news_content']/h1").xpath("string(.)").get()
            title2 = response.xpath("//*[@id='news_content']/h3[2]").xpath("string(.)").get()
            title=title1+title2
            content = response.xpath("//*[@id='news_content']/cms-content").xpath("string(.)").get()
            url = response.url
            date = re.search('hsrb/(\d+-\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//*[@id='news_content']/cms-content//img/@src").getall()
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
