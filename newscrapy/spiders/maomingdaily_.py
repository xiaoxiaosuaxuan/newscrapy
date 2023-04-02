# -*- coding: utf-8 -*-
from subprocess import call
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "maomingdaily"
    newspapers = "茂名日报"
    allowed_domains = ['paper.mm111.net']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://paper.mm111.net/shtml/mmrb/{date}/vA1.shtml"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://paper.mm111.net/shtml/mmrb/20220122/vA4.shtml
    rules = (
        Rule(LinkExtractor(allow=('\d+/vA\w+.shtml'))),
        Rule(LinkExtractor(allow=('\d+/\w+.shtml')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='detailCon']//h1").xpath('string(.)').get()
            content = response.xpath("//*[@id='content_div']/p[@align='left']/font").xpath("string(.)").get()
            url = response.url
            date = re.search("mmrb/(\d+)", url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
            imgs = response.xpath("//div[@id='article_img_marquee']//img/@src").getall()
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
