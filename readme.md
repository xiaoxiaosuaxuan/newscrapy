#### 项目框架
打开总文件夹后，需要关心的有以下几个目录和文件：
```
newscrapy\ : scrapy的项目目录
    ---newscrapy\spiders\: 编写的爬虫目录
results\ : 爬取的结果目录
test.py : 一个用来运行爬虫的脚本
```

为了运行爬虫，需要首先安装一些库，如``pip install scrapy, pymongo``，其他可能依赖的库请自行安装。


#### 一个简单测试
当安装必要的库后，可以运行 ``test.py``，如果成功，你会看到终端的输出，并且``\results``目录里对应的结果文件里可以看到爬取的内容。

``test.py``的实质是在命令行调用：``scrapy crawl 报纸名 -a start=开始日期 -a end=结束日期``， 因此你可以修改该文件中的``name, start, end``来指定具体的爬虫行为。

#### spiders
``newscrapy\spiders``是爬虫目录，为不同报纸编写的爬虫会放在该目录下。该目录下已经有几个编写好的爬虫，例如``baotoudaily.py``是为《包头日报》编写的爬虫文件。

每个爬虫文件中都会定义一个继承自``CrawlSpider``的爬虫类，这个类规定了爬取的规则，即：
* 需要爬取哪些链接
* 每个链接对应的页面需要爬取哪些内容


#### 实例说明
下面以 ``workerdaily.py``中定义的爬虫来说明如何编写一个爬虫类：
```py
class mySpider(CrawlSpider):
    name = "workerdaily"
    newspapers = "工人日报"
    allowed_domains = ['www.workercn.cn']

    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y/%m/%d")
        template = "https://www.workercn.cn/papers/grrb/{date}/1/page.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('grrb/\d+/\d+/\d+/\d+/page.html'), restrict_xpaths="//*[@id='pageTitle']")),
        Rule(LinkExtractor(allow=('grrb/\d+/\d+/\d+/\d+/news-\d+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title1 = response.xpath("//*[@id='pretitle']").xpath("string(.)").get()
            title2 = response.xpath("//*[@id='ctitle']").xpath("string(.)").get()
            title = title1 + ' ' + title2
            content = response.xpath("//*[@id='ccontent']").xpath('string(.)').get()
            url = response.url
            date = re.search('grrb/(\d+/\d+/\d+)/', url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath("//*[@id='imgs']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html  =response.text
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
```
1. 类名为mySpider，继承自``CrawlSpider``。为了统一，所有的爬虫类名都为``mySpider``。
2. 属性：
   * name，定义了这个爬虫的名称（请与爬虫的类名区分），必须是唯一的。命令``scrapy crawl 报纸名 -a start=开始日期 -a end=结束日期``中，使用的报纸名即name。**为了统一，一个爬虫的name应与其所在的python文件名相同**。
   * newspaper，即该爬虫对应报纸的中文名称。
   * allowed_domains，爬虫允许爬取的域名范围。
3. start_request: 这个函数规定了爬虫的种子。
4. rules：规定了当我们爬取到一个页面时，这个页面上的哪些链接会被继续爬取，以及不同的链接被爬取到后会执行哪些操作。我们定义的规则都是用来提取链接的，因此都形如``Rule(LinkExtractor(...))``。参数的含义如下：
   * allow: 用正则表达式定义了链接的格式
   * callback: 是一个回调函数，定义了爬取到对应url的页面后，对该页面执行的操作。具体来说，scrapy爬取到的页面被包装成一个response对象，作为参数传递给这个函数。
   * restrict_xpath: 定义在页面的哪一部分提取url，不是必须的。
  
    这里我们定义了两条规则，这也是日报类爬虫大多数的情况。为什么定义两条规则？因为并非所有的页面都有内容要提取，例如[页面1](https://www.workercn.cn/papers/grrb/2022/10/28/1/page.html)对应的是第一条规则，这个页面是日报的版面，上面没有新闻内容，我们只需要提取页面上的链接，不需要解析页面的内容，也不需要回调函数。 而[页面2](https://www.workercn.cn/papers/grrb/2022/10/28/1/news-4.html)对应的是第二条规则，我们需要解析内容，因此也需要回调函数。

5. parse_item：这个函数即解析页面时的回调函数。它的参数response是scrapy爬取到的网页，可以理解成html页面的头结点。在这个函数里，我们通过xpath语法来解析html文件，获取所需要的内容，如标题，正文等。

#### 推荐阅读
1. scrapy的官方教程：https://docs.scrapy.org/en/latest/intro/tutorial.html
2. xpath教程：https://www.runoob.com/xpath/xpath-tutorial.html