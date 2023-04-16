# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "baojidaily"
    newspapers = "宝鸡日报"
    allowed_domains = ['bjrb.joyhua.cn']
#http://bjrb.joyhua.cn/bjrb/20230413/html/index.htm
#http://bjrb.joyhua.cn/bjrb/20230413/html/page_03.htm
#http://bjrb.joyhua.cn/bjrb/20230413/html/content_20230413001002.htm
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://bjrb.joyhua.cn/bjrb/{date}/html/index.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('index.htm'))),
        Rule(LinkExtractor(allow=('page_\w+.htm'))),
        Rule(LinkExtractor(allow=('content_\w+.htm')),callback='parse_item')
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='bmnr_con']")
            biaoti = body.xpath(".//div[@class='bmnr_con_biaoti']").get()
            yinti = body.xpath(".//div[@class='bmnr_con_yinti']").get()
            title = biaoti + yinti
            content = body.xpath(".//div[@class='bmnr_con_con']/div[@id='zoom']").xpath("string(.)").get()
            imgs = body.xpath(".//div[@class='bmnr_con_con']/div[@id='zoom']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            url = response.url
            date = re.search('bjrb/(\d+)', url).group(1)
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
