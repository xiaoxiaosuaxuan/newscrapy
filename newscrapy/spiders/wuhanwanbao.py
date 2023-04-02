# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse
import unicodedata


class mySpider(CrawlSpider):
    name = "wuhanwanbao"
    newspapers = "武汉晚报"
    allowed_domains = ['whwb.cjn.cn']
#仅包括2023年2月以后的部分
    
    def start_requests(self):    
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://whwb.cjn.cn/html/{date}/node_73.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://whwb.cjn.cn/html/2023-02/08/node_73.htm
#http://whwb.cjn.cn/html/2023-02/08/content_252327.htm
    rules = (
        Rule(LinkExtractor(allow=('node_\w+.htm'))),
        Rule(LinkExtractor(allow=('content_\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@class='text_c']/h3").xpath("string(.)").get()
            title2=response.xpath("//div[@class='text_c']/h1").xpath("string(.)").get()
            title3=response.xpath("//div[@class='text_c']/h2").xpath("string(.)").get()
            title=title1+title2+title3
            content = response.xpath("//div[@id='articleContent']").xpath("string(.)").get()
            content = unicodedata.normalize("NFKC", content)
            url = response.url
            date = re.search('html/(\d+-\d+/\d+)/content', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='c_c']//img/@src").getall()
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
