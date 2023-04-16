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
    name = "huashangbao"
    newspapers = "华商报"
    allowed_domains = ['ehsb.hspress.net']
    #http://ehsb.hspress.net/shtml/hsb/20230415/vA1.shtml
    #http://ehsb.hspress.net/shtml/hsb/20230415/957587.shtml
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://ehsb.hspress.net/shtml/hsb/{date}/vA1.shtml"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('\d+/vA\w+.shtml'))),
        Rule(LinkExtractor(allow=('\d+/\w+.shtml')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//div[@class='content']/h1").xpath("string(.)").get()
            title2 = response.xpath("//div[@class='content']/h5").xpath("string(.)").get()
            #title = title1 + ' ' + title2
            content = response.xpath("//div[@class='para']").xpath("string(.)").get()
            url = response.url
            date = re.search("hsb/(\d+)", url).group(1)
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
