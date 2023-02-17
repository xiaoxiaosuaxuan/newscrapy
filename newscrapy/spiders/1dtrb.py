from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "dtrb"
    newspapers = "大同日报"
    allowed_domains = ['epaper.dtnews.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://epaper.dtnews.cn/dtrb/html/{date}/node_1.htm?v=1"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node_\d+.htm'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content_\d+_\d+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//table[@class='wz']")
            title = body.xpath(".//td[@class='font01']/founder-title").xpath("string(.)").get()
            content = body.xpath(".//div[@id='ozoom']//founder-content/p").xpath("string(.)").getall()
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = body.xpath(".//table[@id='newspic']//img/@src").getall()
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