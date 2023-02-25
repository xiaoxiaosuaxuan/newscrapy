# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "jiamusidaily"
    newspapers = "佳木斯日报"
    allowed_domains = ['szb.jmsxww.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://szb.jmsxww.com/html/szbz/{date}/szbzA1.Html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.jmsxww.com/html/szbz/20220824/Index.Html
#http://szb.jmsxww.com/Html/szbz/20230224/szbzA1.Html
#http://szb.jmsxww.com/html/szbz/20220824/szbzA2.Html
#http://szb.jmsxww.com/html/szbz/20220824/szbz277334.Html
    rules = (
        # Rule(LinkExtractor(allow=('\d+/index.html'))),
        Rule(LinkExtractor(allow=('szbz/\d+/szbzA\w+'))),
        Rule(LinkExtractor(allow=('szbz/\d+/szbz\w+')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath("//td[@height='40']").xpath("string(.)").get()
            content = response.xpath("//div[@id='ozoom']").xpath("string(.)").get(all)
            url = response.url
            date = re.search("szbz/(\d+)", url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
            imgs = response.xpath("//div[@id='copytext']//img/@src").getall()
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
