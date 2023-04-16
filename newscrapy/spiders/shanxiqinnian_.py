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
    name = "shanxiqinnian"
    newspapers = "山西青年报"
    allowed_domains = ['www.sxqnb.com.cn']
    #http://www.sxqnb.com.cn/shtml/sxqnb/20230414/v06.shtml#06
    #http://www.sxqnb.com.cn/shtml/sxqnb/20230414/577605.shtml
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://www.sxqnb.com.cn/shtml/sxqnb/{date}/v01.shtml#01"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('\d+/v\w+.shtml#\w+'))),
        Rule(LinkExtractor(allow=('\d+/\w+.shtml')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@class='show_title1']").xpath("string(.)").get()
            title = response.xpath("//h1[@class='h_title1']").xpath("string(.)").get()
            #title = title1 + ' ' + title2
            content = response.xpath("//div[@class='para']").xpath("string(.)").get()
            url = response.url
            date = re.search("sxqnb/(\d+)", url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
            imgs = response.xpath("//div[@id='article_img_marquee']//a/@href").getall()
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
