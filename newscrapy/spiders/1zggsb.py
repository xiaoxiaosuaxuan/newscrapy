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
    name = "zggsb"
    newspapers = "中国工商报"
    allowed_domains = ['mt.cmrnn.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://mt.cmrnn.com.cn/zggsb/{date}/paper.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('zggsb/\d+/paper.html'))),
        Rule(LinkExtractor(allow=('zggsb/\d+/\d+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("div[@id='article-content']")
            title = body.xpath("//h2").xpath("string(.)").get()
            content = response.xpath("//div[@class='content_p']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("zggsb/(\d+)/\d+", url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
            imgs = response.xpath("//div[@class='content_p']/img/@src").getall()
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