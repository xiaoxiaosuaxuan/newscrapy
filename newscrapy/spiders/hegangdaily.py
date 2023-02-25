# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "hegangdaily"
    newspapers = "鹤岗日报"
    allowed_domains = ['hgrb.dbw.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "https://hgrb.dbw.cn/Html/szbz/{date}/szbzA1.Html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#https://hgrb.dbw.cn/Html/szbz/20210705/szbzA1.Html
#https://hgrb.dbw.cn/Html/szbz/20210705/szbz77514.Html

    rules = (
        # Rule(LinkExtractor(allow=('\d+/index.html'))),
        Rule(LinkExtractor(allow=('szbz/\d+/szbzA\w+'))),
        Rule(LinkExtractor(allow=('szbz/\d+/szbz\w+')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='title']").xpath("string(.)").get()
            content = response.xpath("//div[@class='content']").xpath("string(.)").get(all)
            url = response.url
            date = re.search("szbz/(\d+)", url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
            imgs = response.xpath("//table[@align='center']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html = response.text
        except Exception as e:
            print(e)
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
