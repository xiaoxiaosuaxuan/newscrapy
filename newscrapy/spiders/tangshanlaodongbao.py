# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "tangshanlaodongbao"
    newspapers = "唐山劳动日报"
    allowed_domains = ['epaper.huanbohainews.com.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "https://epaper.huanbohainews.com.cn/tsldrb/pc/col/{date}/node_3.html"
        for d in dates:
            yield FormRequest(template.format(date = d))
#https://epaper.huanbohainews.com.cn/tsldrb/pc/col/202302/22/node_3.html
#https://epaper.huanbohainews.com.cn/tsldrb/pc/content/202302/22/content_57459.html
    rules = (
        Rule(LinkExtractor(allow=('col/\d+/\d+/node_\w+.html'))),
        Rule(LinkExtractor(allow=('content/\d+/\d+/content_\w+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//p[@class='introtitle text-center']").xpath('string(.)').get()
            title2 = response.xpath("//h2[@class='art-title text-center']").xpath('string(.)').get()
            title3=response.xpath("//p[@class='subtitle text-center']").xpath('string(.)').get()
            title = title1 + ' ' + title2 + ' ' + title3
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
