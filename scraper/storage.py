from pymongo import MongoClient
import sys
import time
import locale

cars = [ {'name': 'Audi', 'price': 52642},
    {'name': 'Mercedes', 'price': 57127},
    {'name': 'Skoda', 'price': 9000},
    {'name': 'Volvo', 'price': 29000},
    {'name': 'Bentley', 'price': 350000},
    {'name': 'Citroen', 'price': 21000},
    {'name': 'Hummer', 'price': 41400},
    {'name': 'Volkswagen', 'price': 21600} ]



def insert_posts(posts):
    
    client = MongoClient('mongodb://localhost:27017/')
    with client:
        try:
            db = client['luxurai_backend']

            db['posts'].find_one_and_update({'link': posts['link']}, {"$set": dict(posts)}, upsert=True)
        except:
            print("Unexpected error:", sys.exc_info()[0])


def get_posts(db = 'luxurai_backend'):
    client = MongoClient('mongodb://localhost:27017/')
    with client:
        try:
            record = list(client[db]['posts'].aggregate([{"$sort":{"time":-1}}, {"$limit":1}]))
            if len(record) == 0:
                return None
            locale.setlocale(locale.LC_ALL, 'zh_CN.utf-8')
            return time.strptime(record[0]['time'], '%Y年%m月%d日 %A%p%I:%M')
            #last_time = record[0]
            #for doc in record:
            #    print(doc)
        except:
            print('unexpected error:', sys.exc_info()[0])