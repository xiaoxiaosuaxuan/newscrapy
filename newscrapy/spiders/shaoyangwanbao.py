# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "shaoyangwanbao"
    newspapers = "邵阳晚报"
    allowed_domains = ['szb.shaoyangnews.net']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://szb.shaoyangnews.net/sywb/pc/column/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.shaoyangnews.net/sywb/pc/column/202302/24/node_01.html
#http://szb.shaoyangnews.net/sywb/pc/content/202302/24/content_38108.html
    rules = (
        Rule(LinkExtractor(allow=('pc/column/\d+/\d+/node\w+.html'))),
        Rule(LinkExtractor(allow=('pc/content/\d+/\d+/content\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='PreTitle']").xpath('string(.)').get()
            title2 = response.xpath("//*[@id='Title']").xpath('string(.)').get()
            title3 = response.xpath("//*[@id='SubTitle']").xpath('string(.)').get()
            title = title1 + ' ' + title2+' ' + title3
           
            content = response.xpath("//founder-content").xpath('string(.)').get()
            url = response.url
            date = re.search("content/(\d+/\d+)/", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='attachment']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html = response.text
        except Exception as e:
            return
        
        item = NewscrapyItem()
        item['title'] = title
        # item['author'] = author
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = response.url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item
