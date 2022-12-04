from subprocess import call
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "wanxidaily"
    newspapers = "皖西日报"
    allowed_domains = ['wxrb.luaninfo.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m%d")
        template = "http://wxrb.luaninfo.com/wx/{date}/Page01CJ.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('wx/\d+\d+\d+/Page\d+CJ.htm'))),
        Rule(LinkExtractor(allow=('wx/\d+\d+\d+/Articel\d+ZG.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='neirong']")
            title = body.xpath("//h2").xpath("string(.)").get()
            content = body.xpath("//div[@class='contenttext']").xpath("string(.)").getall()
            url = response.url
            date = re.search("wx/(\d+)/Articel", url).group(1)
            date = '-'.join([date[0:4],date[4:6],date[6:8]])
            imgs = body.xpath("//div[@class='imagelist']//img/@src").getall()
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
