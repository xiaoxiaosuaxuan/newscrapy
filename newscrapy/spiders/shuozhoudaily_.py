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
    name = "shuozhoudaily"
    newspapers = "朔州日报"
    allowed_domains = ['szb.sxsznews.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://szb.sxsznews.com/shtml/szrb/{date}/vA1.shtml"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.sxsznews.com/shtml/index_szrb.shtml
    rules = (
        Rule(LinkExtractor(allow=('\d+/vA\w+.shtml'))),
        Rule(LinkExtractor(allow=('\d+/\w+.shtml')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='detailCon']//h1").xpath('string(.)').get()
            content = response.xpath("//*[@id='content_div']/p[@align='left']/font").xpath("string(.)").get()
            url = response.url
            date = re.search("szrb/(\d+)", url).group(1)
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
