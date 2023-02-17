# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "jilinnongcunbao"
    newspapers = "吉林农村报"
    allowed_domains = ['www.jlncb.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://www.jlncb.cn/jlncb/pc/paper/layout/{date}/node_08.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('paper/layout/\d+/\d+/node\w+.html'))),
        Rule(LinkExtractor(allow=('paper/c/\d+/\d+/content\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title0 = response.xpath("//p[@id='PreTitle']").xpath("string(.)").get()
            title1 = response.xpath("//h2[@id='Title']").xpath("string(.)").get()
            subtitle = response.xpath("//p[@id='SubTitle']").xpath("string(.)").get()
            title = title0 + ' ' + title1 + ' ' + subtitle
            content = response.xpath("//div[@class='content']").xpath("string(.)").get()
            url = response.url
            date = re.search("c/(\d+/\d+)/content", url).group(1)
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
