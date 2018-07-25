# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
import pymysql

class MongoPipelines(object):
    def __init__(self,mongo_uri,mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
                mongo_uri = crawler.settings.get('MONGO_URI'),
                mongo_db = crawler.settings.get('MONGO_DB')
                )
        
    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        
    def process_item(self, item, spider):
        self.db[item.collection].insert(dict(item))
        return item
    
    def close_spider(self,spider):
        self.client.close()

class MysqlPipelines(object):
    def __init__(self,host,user,password,database,port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
    
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
                host = crawler.settings.get('MYSQL_HOST'),
                user = crawler.settings.get('MYSQL_USER'),
                password = crawler.settings.get('MYSQL_PASSWORD'),
                database = crawler.settings.get('MYSQL_DATABASE'),
                port = crawler.settings.get('MYSQL_PORT')
                )
    
    def open_spider(self,spider):
        self.db = pymysql.connect(self.host,self.user,self.password,self.database,
                                  charset='utf8',port=self.port)
        self.cursor = self.db.cursor()
    
    def close_spider(self,spider):
        self.db.close()
    
    def process_item(self,item,spider):
        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%s']*len(data))
        sql = 'INSERT INTO %s (%s) VALUES (%s)'%(item.table,keys,values)
        self.cursor.execute(sql,tuple(data.values()))
        self.db.commit()
        return item