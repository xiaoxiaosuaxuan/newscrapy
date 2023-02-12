from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "beijingqnbao"
    newspapers = "北京青年报"
    allowed_domains = ['epaper.ynet.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://epaper.ynet.com/html/{date}/node_1334.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node_\d+.htm'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content_\d+.htm?')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='rit']")
            foundertitle = body.xpath(".//h1").xpath("string(.)").get()
            subtitle = body.xpath(".//p[@class='fbiaot']").xpath("string(.)").get()
            title = foundertitle+' '+subtitle
            content = body.xpath(".//div[@class='contnt']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = body.xpath(".//div[@class='contnt']//table//img/@src").getall()
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