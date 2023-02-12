from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "fuxiaobao"
    newspapers = "拂晓报"
    allowed_domains = ['www.zgfxnews.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://www.zgfxnews.com/mp/fxb/pc/layout/{date}/node_02.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('mp/fxb/pc/layout/\d+\d+/\d+/node_\d+.html'))),
        Rule(LinkExtractor(allow=('mp/fxb/pc/content/\d+\d+/\d+/content_\d+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='detail-art']")
            foundertitle = body.xpath(".//h2").xpath("string(.)").get()
            subtitle = body.xpath(".//p[@id='SubTitle']").xpath("string(.)").get()
            title = foundertitle+' '+subtitle
            content = body.xpath(".//div[@class='articleMain']//founder-content/p").xpath("string(.)").getall()
            url = response.url
            date = re.search("content/(\d+\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = body.xpath(".//div[@class='attachment']//img/@src").getall()
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