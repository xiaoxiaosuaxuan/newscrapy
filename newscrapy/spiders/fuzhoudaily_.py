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
    name = "fuzhoudaily"
    newspapers = "福州日报"
    allowed_domains = ['mag.fznews.com.cn']
    #
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://mag.fznews.com.cn/fzrb/2022/{date}/{date}_001/{date}_001.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://mag.fznews.com.cn/fzrb/2022/20220828/20220828_001/20220828_001.html
#http://mag.fznews.com.cn/fzrb/2022/20220828/20220828_001/20220828_001_5.htm
    rules = (
        Rule(LinkExtractor(allow=('\d+/\d+/\d+_\w+/\d+_\w+.html'))),
        Rule(LinkExtractor(allow=('\d+/\d+/\d+_\w+/\d+_\w+_\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@class='css_yt']/h3").xpath("string(.)").get()
            title2 = response.xpath("//div[@class='css_yt']/h1").xpath("string(.)").get()
            title = title1 + ' ' + title2
            content = response.xpath("//div[@id='zhenwenzone']//p").xpath("string(.)").get(all)
            url = response.url
            date = re.search("/(\d+)/", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            imgs = response.xpath("//div[@align='center']/p/img/@src").getall()
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