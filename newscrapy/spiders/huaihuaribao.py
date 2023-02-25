# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "huaihuaribao"
    newspapers = "怀化日报"
    allowed_domains = ['paper.0745news.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://paper.0745news.cn/hhrbpc/{date}/l01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://paper.0745news.cn/hhrbpc/202208/31/l01.html
#http://paper.0745news.cn/hhrbpc/202208/31/c106414.html
    rules = (
        Rule(LinkExtractor(allow=('\d+/\d+/l\w+.html'))),
        Rule(LinkExtractor(allow=('\d+/\d+/c\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//p[@class='introtitle text-center']").xpath('string(.)').get(all)
            title2 = response.xpath("//h2[@class='art-title text-center']").xpath('string(.)').get()
            title3 = response.xpath("//p[@class='subtitle text-center']").xpath('string(.)').get()
            title = title1 + ' ' + title2+ ' ' + title3
            content = response.xpath("//founder-content").xpath('string(.)').get(all)
            url = response.url
            date = re.search("hhrbpc/(\d+/\d+)/", url).group(1)
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
