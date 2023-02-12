# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "huhehaotedaily"
    newspapers = "呼和浩特日报"
    allowed_domains = ['szb.saibeinews.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://szb.saibeinews.com.cn/rb/page/{date}/node_2.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('rb/page/\d+-\d+/\d+/node\w+.htm'))),
        Rule(LinkExtractor(allow=('rb/page/\d+-\d+/\d+/content\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//td[@style='padding-left: 6px;padding-top:10px;padding-bottom:10px;']").xpath("string(.)").get()
            content = response.xpath("//td[@style='PADDING:0px 30px 0px 10px; FONT-SIZE: 14px; LINE-HEIGHT: 21px']").xpath("string(.)").get()
            url = response.url
            date = re.search("page/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//table[@bgcolor='#d8d9bd']//img/@src").getall()
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
