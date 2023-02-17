from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "guojidaily"
    newspapers = "国际日报"
    allowed_domains = ['epaper.guojiribao.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://epaper.guojiribao.com/shtml/gjrb/{date}/vA1.shtml"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('shtml/gjrb/\d+/vA\d+.shtml'))),
        Rule(LinkExtractor(allow=('shtml/gjrb/\d+/\d+.shtml')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='con4']")
            title = body.xpath(".//h3").xpath("string(.)").get()
            content = body.xpath(".//div[@class='con3 fgrey12']//font").xpath("string(.)").get()
            url = response.url
            date = re.search("gjrb/(\d+)/\d+", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            imgs = body.xpath(".//div[@class='con3 fgrey12']//img/@src").getall()
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