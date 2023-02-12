# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "xianningdaily"
    newspapers = "咸宁日报"
    allowed_domains = ['szb.xnnews.com.cn']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://szb.xnnews.com.cn/xnrb/html/{date}/node_5.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.xnnews.com.cn/xnrb/html/2022-08/30/node_5.htm
#http://szb.xnnews.com.cn/xnrb/html/2022-08/30/content_628531.htm
    rules = (
        Rule(LinkExtractor(allow=('node\w+\.htm'))),
        Rule(LinkExtractor(allow=('content\w+\.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("/html/body/div[1]/div/div[3]/div[3]/table/tbody/tr[1]/td").xpath("string(.)").get()
            title2 = response.xpath("/html/body/div[1]/div/div[3]/div[3]/table/tbody/tr[2]/td").xpath("string(.)").get()
            title=title1+title2
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search('html/(\d+-\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='m5']//img/@src").getall()
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
