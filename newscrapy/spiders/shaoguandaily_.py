# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "shaoguandaily"
    newspapers = "韶关日报"
    allowed_domains = ['sgrb.sgxw.cn']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://sgrb.sgxw.cn/html/{date}/node_1.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://sgrb.sgxw.cn/html/2021-04/19/node_99447.htm
#http://sgrb.sgxw.cn/html/2021-04/19/content_100247_13275513.htm
    rules = (
        Rule(LinkExtractor(allow=('node_\w+\.htm'))),
        Rule(LinkExtractor(allow=('content_\w+\.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='bmnr_con']")
            biaoti = body.xpath(".//div[@class='bmnr_con_biaoti']//text()").get()
            yinti = body.xpath(".//div[@class='bmnr_con_yinti']/text()").get()
            title = biaoti + yinti
            content = body.xpath(".//founder-content").xpath("string(.)").get()
            imgs = body.xpath(".//table[@id='newspic']//img").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            url = response.url
            date = re.search('html/(\d+-\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
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
