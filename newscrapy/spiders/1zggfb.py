from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "zggfb"
    newspapers = "中国国防报"
    allowed_domains = ['www.81.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "http://www.81.cn/gfbmap/content/{date}/node_22.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('content/\d+-\d+/\d+/node_\d+.htm'))),
        Rule(LinkExtractor(allow=('content/\d+-\d+/\d+/content_\d+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath(".//p[@class='introtitle']").xpath("string(.)").get()
            title2 = response.xpath(".//h2[@id='APP-Title']").xpath("string(.)").get()
            title3 = response.xpath(".//p[@class='author']").xpath("string(.)").get()
            title = title1+title2+title3
            content = response.xpath(".//div[@class='article-content']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("content/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//div[@class='attachment']//img/@src").getall()
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