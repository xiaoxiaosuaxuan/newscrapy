# -*- coding: utf-8 -*-
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "zhanjiangwanbao"
    newspapers = "湛江晚报"
    allowed_domains = ['szb.gdzjdaily.com.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://szb.gdzjdaily.com.cn/zwrb/html/{date}/node_2.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))
#http://szb.gdzjdaily.com.cn/zjwb/html/2015-05/05/content_.htm
#http://szb.gdzjdaily.com.cn/zjwb/html/2015-05/05/node_181.htm
    rules = (
        Rule(LinkExtractor(allow=('/node_\w+.htm'))),
        Rule(LinkExtractor(allow=('/content_\d+.htm')),callback='parse_item')
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//tr[@valign='top']/td[@style='color: #827E7B;']").xpath("string(.)").get()
            title2 = response.xpath("//tr[@valign='top']/td[@style='color: #0205FF;']").xpath("string(.)").get()
            title3 = response.xpath("//tr[@valign='top']/td[@style='color: #827E7B;']").xpath("string(.)").get()
            title4 = response.xpath("//tr[@valign='top']/td[@style='color: #827E7B;']").xpath("string(.)").get()
            title = title1 + ' ' + title2 + ' ' + title3 + ' ' + title4
            content = response.xpath("//div[@id='ozoom']/content").xpath("string(.)").get(all)
            imgs = response.xpath("//table[@bgcolor='#d8d9bd']//img/@src").getall()
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
