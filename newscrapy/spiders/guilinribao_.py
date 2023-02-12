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
    name = "guilinribao"
    newspapers = "桂林日报"
    allowed_domains = ['epaper.guilinlife.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://epaper.guilinlife.com/glrbpc/glrb/{date}/Page01BC.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('\d+/Page\w+.htm'))),
        Rule(LinkExtractor(allow=('\d+/Articel\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@class='neirong']//h3").xpath("string(.)").get()
            title2 = response.xpath("//div[@class='neirong']//h2").xpath("string(.)").get()
            title3 = response.xpath("//div[@class='neirong']//h4").xpath("string(.)").get()
            title = title1 +" "+ title2 + " " + title3
            content = response.xpath("//span[@id='contenttext']").xpath("string(.)").get()
            url = response.url
            date = re.search("glrb/(\d+)/Articel", url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
            imgs = response.xpath("//span[@id='imagelist']/img/@src").getall()
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
