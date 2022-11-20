# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from textwrap import fill
import pymongo

filepath = "result"

class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[spider.name]
    
    def close_spider(self, spider):
        self.client.close()
        
    def process_item(self, item, spider):
        self.collection.insert_one(ItemAdapter(item).asdict())
        return item
    
class TxtPipeline:
    def open_spider(self, spider):
        filepath = 'results/' + spider.name + '_result.txt'
        self.file = open(filepath, 'a+', encoding='utf-8')
        

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        try:
            self.file.write("date: " + f"{item['date']}".strip() + "\n")
            self.file.write("url: "  + f"{item['url']} \n")
            self.file.write("newspaper: " + f"{item['newspaper']} ".strip() + "\n")
            self.file.write("title: " + f"{item['title']}".strip() + "\n")
            self.file.write(fill("content: " + f"{item['content']}".strip() + "\n") + "\n")
            self.file.write("imgs: " + f"{item['imgs']}".strip() + "\n\n\n\n")
        except Exception as e:
            print(e)
        return item

