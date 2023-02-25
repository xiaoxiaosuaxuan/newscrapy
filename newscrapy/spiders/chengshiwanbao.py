# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "chengshiwanbao"
    newspapers = "城市晚报"
    allowed_domains = ['www.cswbszb.com']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://www.cswbszb.com/cswb/pc/paper/layout/{date}/node_A02.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://www.cswbszb.com/cswb/pc/paper/layout/202212/16/node_A01.html
#http://www.cswbszb.com/cswb/pc/paper/c/202212/16/content_118410.html
    rules = (
        Rule(LinkExtractor(allow=('paper/layout/\d+/\d+/node_\w+.html'))),
        Rule(LinkExtractor(allow=('paper/c/\d+/\d+/content_\w+.html')),callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='PreTitle']").xpath('string(.)').get()
            title2 = response.xpath("//*[@id='Title']").xpath('string(.)').get()
            title3 = response.xpath("//*[@id='SubTitle']").xpath('string(.)').get()
            title = title1 + ' ' + title2+ ' ' + title3
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search('c/(\d+/\d+)/', url).group(1)
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
