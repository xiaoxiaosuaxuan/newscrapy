# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "pingdingshanwanbao"
    newspapers = "平顶山晚报"
    allowed_domains = ['epaper.pdsxww.com']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://epaper.pdsxww.com/pdswb/html/{date}/node_42.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://epaper.pdsxww.com/pdswb/html/2022-08/18/node_42.htm
#http://epaper.pdsxww.com/pdswb/html/2022-08/18/content_364607.htm
    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node\w+.htm'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1=response.xpath("//td[@align='center']/span").xpath("string(.)").get()
            title2 = response.xpath("//td[@align='center']/strong").xpath("string(.)").get()
            title=title1+title2
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search('html/(\d+-\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//td[@class='px12c']//img/@src").getall()
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
