# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "suizhoudaily"
    newspapers = "随州日报"
    allowed_domains = ['szrb.sz-news.com.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://szrb.sz-news.com.cn/szrb/{date}/html/index.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szrb.sz-news.com.cn/szrb/20230128/html/index.htm
#http://szrb.sz-news.com.cn/szrb/20230128/html/page_01.htm
#http://szrb.sz-news.com.cn/szrb/20230128/html/content_20230128002002.htm
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
            imgs = response.xpath("//div[@id='zoom']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            url = response.url
            date = re.search('szrb/(\d+)/html', url).group(1)
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
