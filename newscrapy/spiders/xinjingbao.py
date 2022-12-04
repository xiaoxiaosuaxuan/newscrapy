from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "xinjingbao"
    newspapers = "新京报"
    allowed_domains = ['epaper.bjnews.com.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://epaper.bjnews.com.cn/html/{date}/node_1.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node_\d+.htm'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content_\d+.htm?')),callback='parse_item')
    )

    def parse_item(self, response):
        try:
            biaoti = response.xpath("//div[@class='rit']/p[@class='pdec']//text()").get()
            yinti = response.xpath("//div[@class='rit']/h1//text()").get()
            title = biaoti + yinti
            content = response.xpath("//div[@class='contnt']//founder-content//p").xpath("string(.)").getall()
            imgs = response.xpath("//div[@class='tqnr']//img/@src").getall()
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
