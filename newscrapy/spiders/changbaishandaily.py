# -*- coding: utf-8 -*-
from scrapy import FormRequest
import regex as re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "changbaishandaily"
    newspapers = "长白山日报"
    allowed_domains = ['szb.jlbstv.com']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://szb.jlbstv.com/pc/layout/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.jlbstv.com/pc/layout/202212/16/node_01.html
#http://szb.jlbstv.com/pc/content/202212/16/content_47811.html
    rules = (
        Rule(LinkExtractor(allow=('layout/\d+/\d+/node_\w+.html'))),
        Rule(LinkExtractor(allow=('content/\d+/\d+/content_\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//div[@class='intro']").xpath('string(.)').get()
            title2 = response.xpath("//*[@id='ScroLeft']/div[1]/h3").xpath('string(.)').get()
            title3 = response.xpath("//div[@class='sub']").xpath('string(.)').get()
            title = title1 + ' ' + title2+' '+title3
            content = response.xpath("//founder-content").xpath('string(.)').get()
            url = response.url
            date = re.search("content/(\d+/\d+)/", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@class='pic']//img/@src").getall()
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
