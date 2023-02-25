# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "tianzhongwanbao"
    newspapers = "天中晚报"
    allowed_domains = ['tzwb.zmdnews.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://tzwb.zmdnews.cn/tzwb/{date}/html/index.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://tzwb.zmdnews.cn/tzwb/20220825/html/index.htm
#http://tzwb.zmdnews.cn/tzwb/20220825/html/page_01.htm
#http://tzwb.zmdnews.cn/tzwb/20220825/html/content_79379.htm
    rules = (
        Rule(LinkExtractor(allow=('\d+/html/index.htm'))),
        Rule(LinkExtractor(allow=('\d+/html/page_\w+.htm'))),
        Rule(LinkExtractor(allow=('\d+/html/content_\w+.htm')),callback='parse_item')
    )

    def parse_item(self, response):
        try:
            biaoti = response.xpath("//div[@class='bmnr_con_biaoti']").xpath("string(.)").get()
            yinti = response.xpath("//div[@class='bmnr_con_yinti']").xpath("string(.)").get()
            futi = response.xpath("//div[@class='bmnr_con_futi']").xpath("string(.)").get()
            title = biaoti + yinti+futi
            content = response.xpath("//div[@id='zoom']").xpath("string(.)").get()
            imgs = response.xpath("//div[@id='zoom']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            url = response.url
            date = re.search('tzwb/(\d+)/html', url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
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
