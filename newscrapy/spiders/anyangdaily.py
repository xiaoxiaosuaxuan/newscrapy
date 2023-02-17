# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "anyangdaily"
    newspapers = "安阳日报"
    allowed_domains = ['www.ayrbs.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "https://www.ayrbs.com/szb/pc/column/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#https://www.ayrbs.com/szb/pc/column/202208/20/node_01.html
#https://www.ayrbs.com/szb/pc/content/202208/20/content_11343.html
    rules = (
        Rule(LinkExtractor(allow=('column/\d+/\d+/node_\w+.html'))),
        Rule(LinkExtractor(allow=('content/\d+/\d+/content_\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='PreTitle']").xpath('string(.)').get()
            title2 = response.xpath("//*[@id='Title']").xpath('string(.)').get()
            title = title1 + ' ' + title2
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
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = response.url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item
