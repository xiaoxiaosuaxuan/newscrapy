
# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "taizhouwanbao"
    newspapers = "台州晚报"
    allowed_domains = ['paper.taizhou.com.cn']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://paper.taizhou.com.cn/taizhou/tzwb/pc/layout/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('taizhou/tzwb/pc/layout/\d+/\d+/node\w+.html'))),
        Rule(LinkExtractor(allow=('taizhou/tzwb/pc/content/\d+/\d+/content\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='detail-art']").xpath("string(.)").get()
            content = response.xpath("//div[@class='content']").xpath("string(.)").get()
            url = response.url
            date = re.search('content/(\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
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

