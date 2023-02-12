# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "haerbindaily"
    newspapers = "哈尔滨日报"
    allowed_domains = ['harbin.joyhua.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://harbin.joyhua.cn/hebrb/{date}/html/index.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://harbin.joyhua.cn/hebrb/20221204/html/index.htm
#http://harbin.joyhua.cn/hebrb/20221204/html/content_20221204001001.htm
    rules = (
        Rule(LinkExtractor(allow=('\d+/html/index.htm'))),
        Rule(LinkExtractor(allow=('\d+/html/page_\d+.htm'))),
        Rule(LinkExtractor(allow=('\d+/html/content_\d+.htm')),callback='parse_item')
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='bmnr_con']")
            biaoti = body.xpath(".//div[@class='bmnr_con_biaoti']//text()").get()
            yinti = body.xpath(".//div[@class='bmnr_con_yinti']/text()").get()
            title = biaoti + yinti
            content = body.xpath(".//div[@class='bmnr_con_con']").xpath("string(.)").get()
            imgs = body.xpath(".//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            url = response.url
            date = re.search('hebrb/(\d+)/html', url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
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
