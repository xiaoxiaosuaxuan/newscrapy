# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "xiangtandaily"
    newspapers = "湘潭日报"
    allowed_domains = ['xtrb.xtol.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://xtrb.xtol.cn/xtrbpc/column/{date}/lA01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://xtrb.xtol.cn/xtrbpc/column/202203/17/lA01.html
#http://xtrb.xtol.cn/xtrbpc/content/202203/17/c68407.html
    rules = (
        Rule(LinkExtractor(allow=('column/\d+/\d+/\w+.html'))),
        Rule(LinkExtractor(allow=('content/\d+/\d+/\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='PreTitle']").xpath('string(.)').get()
            title2 = response.xpath("//*[@id='Title']").xpath('string(.)').get()
            title3 = response.xpath("//*[@id='SubTitle']").xpath('string(.)').get()
           
            title = title1 + ' ' + title2 + title3
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
