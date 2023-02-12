# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "luoyangdaily"
    newspapers = "洛阳日报"
    allowed_domains = ['lyrb.lyd.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://lyrb.lyd.com.cn/html2/{date}/node_4.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://lyrb.lyd.com.cn/html2/2022-08/20/content_311226.htm
#http://lyrb.lyd.com.cn/html2/2022-08/20/node_4.htm
    rules = (
        Rule(LinkExtractor(allow=('html2/\d+-\d+/\d+/node\w+.htm'))),
        Rule(LinkExtractor(allow=('html2/\d+-\d+/\d+/content\w+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1=response.xpath("//td[@align='center']/span").xpath("string(.)").get()
            title2 = response.xpath("//td[@align='center']/strong").xpath("string(.)").get()
            title=title1+title2
            content = response.xpath("//founder-content").xpath("string(.)").get()
            url = response.url
            date = re.search("html2/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//table[@bgcolor='#FFFFFF']//img/@src").getall()
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
