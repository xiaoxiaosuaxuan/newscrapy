# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "luohedaily"
    newspapers = "漯河日报"
    allowed_domains = ['rb.lhrb.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://rb.lhrb.com.cn/html/{date}/node_1.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://rb.lhrb.com.cn/html/2022-11/07/node_1.htm
#http://rb.lhrb.com.cn/html/2022-11/07/content_133216.htm
    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node\w+.htm'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@align='center']//tbody").xpath("string(.)").get()
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//table[@bgcolor='#FFFFFF']//img/@src").getall()
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
