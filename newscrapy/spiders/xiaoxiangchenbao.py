# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "xiaoxiangchenbao"
    newspapers = "潇湘晨报"
    allowed_domains = ['epaper.xxcb.cn']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://epaper.xxcb.cn/xxcba/html/{date}/node_106.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://epaper.xxcb.cn/xxcba/html/2022-09/04/node_106.htm
#http://epaper.xxcb.cn/xxcba/html/2022-09/04/content_3092534.htm
    rules = (
        Rule(LinkExtractor(allow=('node\w+\.htm'))),
        Rule(LinkExtractor(allow=('content\w+\.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@class='biaot']/h1").xpath("string(.)").get()
            title2 = response.xpath("//div[@class='biaot']/p").xpath("string(.)").get()
            title=title1+title2
            content = response.xpath("//div[@id='neir']").xpath("string(.)").get()
            url = response.url
            date = re.search('html/(\d+-\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//table[@bgcolor='#efefef']//img/@src").getall()
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
