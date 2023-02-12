# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "yueyangwanbao"
    newspapers = "岳阳晚报"
    allowed_domains = ['papers.803.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "https://papers.803.com.cn/cjxxb/{date}/node_2.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#https://papers.803.com.cn/cjxxb/2022-09/01/node_2.html
#https://papers.803.com.cn/cjxxb/2022-09/01/content_991180038.html
    rules = (
        Rule(LinkExtractor(allow=('cjxxb/\d+-\d+/\d+/node\w+.htm'))),
        Rule(LinkExtractor(allow=('cjxxb/\d+-\d+/\d+/content\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='news_content']/h1").xpath("string(.)").get()
            title2 = response.xpath("//*[@id='news_content']/h3[2]").xpath("string(.)").get()
            title=title1+title2
            content = response.xpath("//cms-content").xpath("string(.)").get()
            url = response.url
            date = re.search("cjxxb/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//cms-content//img/@src").getall()
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
