# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "heilongjiangdaily"
    newspapers = "黑龙江日报"
    allowed_domains = ['epaper.hljnews.cn']

    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://epaper.hljnews.cn/hljrb/pc/layout/{date}/node_08.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://epaper.hljnews.cn/hljrb/pc/layout/202012/14/node_08.html
#http://epaper.hljnews.cn/hljrb/pc/con/202012/14/content_6143.html
    rules = (
        Rule(LinkExtractor(allow=('layout/\d+/\d+/\w+.html'))),
        Rule(LinkExtractor(allow=('con/\d+/\d+/content_\w+.html')),callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='ScroLeft']/div[1]/div[1]").xpath("string(.)").get()
            title2 = response.xpath("//*[@id='ScroLeft']/div[1]/h3").xpath("string(.)").get()
            title= title1+title2
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search('con/(\d+/\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//*[@class='pic']//img/@src").getall()
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
