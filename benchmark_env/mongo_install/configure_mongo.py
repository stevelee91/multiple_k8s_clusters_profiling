import pymongo
from pymongo import MongoClient

conn = MongoClient('127.0.0.1')
db = conn.test_db
collect = db.collect
doc1 = {'num':'1', 'name':'shlee', 'phone':'010-8999-1235', 'age':35}
collect.insert(doc1)


db.test_db.save
