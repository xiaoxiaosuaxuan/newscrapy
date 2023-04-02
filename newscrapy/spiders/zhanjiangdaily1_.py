# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "zhanjiangdaily1"
    newspapers = "湛江日报"
    allowed_domains = ['szb.gdzjdaily.com.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://szb.gdzjdaily.com.cn/zjrb/html/{date}/node_2.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.gdzjdaily.com.cn/zjrb/html/2015-05/06/content_.htm
#http://szb.gdzjdaily.com.cn/zjrb/html/2015-05/06/node_181.htm
    rules = (
        Rule(LinkExtractor(allow=('/node_\w+.htm'))),
        Rule(LinkExtractor(allow=('/content_\d+.htm')),callback='parse_item')
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='cont']")
            biaoti = body.xpath(".//p[@class='yinti']").xpath("string(.)").get()
            yinti = body.xpath(".//h1").xpath("string(.)").get()
            title = biaoti + yinti
            content = body.xpath(".//div[@id='ozoom']/content").xpath("string(.)").get(all)
            imgs = body.xpath(".//div[@id='ozoom']//img").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
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
