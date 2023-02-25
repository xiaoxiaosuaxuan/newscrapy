# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "jinzhoudaily"
    newspapers = "鄞州日报"
    allowed_domains = ['yzrbepaper.cnnb.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://yzrbepaper.cnnb.com.cn/html/{date}/node_3091.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://yzrbepaper.cnnb.com.cn/html/2022-08/25/node_3091.htm
#http://yzrbepaper.cnnb.com.cn/html/2022-08/25/content_3091_6639704.htm
    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node_\w+.htm'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content_\w+_\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//td[@class='font01']").xpath("string(.)").get()
            title2=response.xpath("//founder-title").xpath("string(.)").get()
            title3 = response.xpath("//td[@class='font02']").xpath("string(.)").get()
            title=title1+title2+title3
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//table[@id='newspic']//img/@src").getall()
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
