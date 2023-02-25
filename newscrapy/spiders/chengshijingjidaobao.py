# -*- coding: utf-8 -*-
from scrapy import FormRequest
import regex as re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "chengshijingjidaobao"
    newspapers = "城市经济导报"
    # allowed_domains = ['epaper.wuhunews.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://epaper.xiancn.com/csjjdb/pc/html/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://epaper.xiancn.com/csjjdb/pc/html/202208/15/node_01.html
#https://xafbapp.xiancn.com/csjjdb/pc/html/202208/15/content_123423.html
    rules = (
        Rule(LinkExtractor(allow=('html/\d+/\d+/node_\w+.html'))),
        Rule(LinkExtractor(allow=('html/\d+/\d+/\content_\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='PreTitle']").xpath('string(.)').get()
            title2 = response.xpath("//*[@id='Title']").xpath('string(.)').get()
            title3=response.xpath("//*[@id='SubTitle']").xpath('string(.)').get()
            title = title1 + ' ' + title2 + ' ' + title3
            content = response.xpath("//founder-content").xpath('string(.)').get()
            url = response.url
            date = re.search("html/(\d+/\d+)/", url).group(1)
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
