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
    name = "shiyousb"
    newspapers = "石油商报"
    allowed_domains = ['news.cnpc.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://news.cnpc.com.cn/epaper/sysb/{date}/index.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('epaper/sysb/\d+/index.htm'))),
        Rule(LinkExtractor(allow=('epaper/sysb/\d+/\d+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//article_title").xpath("string(.)").get()
            content = response.xpath("//con").xpath("string(.)").getall()
            url = response.url
            date = re.search("sysb/(\d+)/\d+", url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
            imgs = response.xpath("//table[@cellspacing='5']//img/@src").getall()
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