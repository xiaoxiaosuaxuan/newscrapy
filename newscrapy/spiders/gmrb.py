from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "gmrb"
    newspapers = "光明日报"
    allowed_domains = ['epaper.gmw.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "https://epaper.gmw.cn/gmrb/html/{date}/nbs.D110000gmrb_01.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('gmrb/html/\d+-\d+/\d+/nbs'))),
        Rule(LinkExtractor(allow=('gmrb/html/\d+-\d+/\d+/nw')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='text_c']")
            title = body.xpath(".//h1").xpath("string(.)").get()
            content = body.xpath(".//div[@id='ozoom']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/nw", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = body.xpath(".//table[@class='c_c']//img/@src").getall()
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