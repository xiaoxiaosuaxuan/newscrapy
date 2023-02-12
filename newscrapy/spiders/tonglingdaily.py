from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "tonglingdaily"
    newspapers = "铜陵日报"
    allowed_domains = ['szb.tlnews.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://szb.tlnews.cn/tlrb/tlrb/pc/layout/{date}/node_A01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('tlrb/tlrb/pc/layout/\d+\d+/\d+/node_\w+\d+.html'))),
        Rule(LinkExtractor(allow=('tlrb/tlrb/pc/con/\d+\d+/\d+/content_\d+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='caption']")
            intro_title = body.xpath(".//font[@id='intro-title']").xpath("string(.)").get()
            main_title = body.xpath(".//font[@id='main-title']").xpath("string(.)").get()
            sub_title = body.xpath(".//font[@id='sub-title']").xpath("string(.)").get()
            title = intro_title+main_title+sub_title
            content = response.xpath("//div[@id='content']//founder-content/p").xpath("string(.)").getall()
            url = response.url
            date = re.search("con/(\d+\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath("//div[@id='content']//img/@src").getall()
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
