from pymongo import MongoClient
import sys
import time
import locale
from simple_rest_client.api import API

restclient = API(
    api_root_url='https://botadmin.luxurai.com/',
    #api_root_url='http://localhost:3030/',
    params={},
    headers={},
    timeout=2,
    append_slash=False,
    json_encode_body=True,
)
restclient.add_resource(resource_name='helpbuys')
collection = 'test'

def rest_insert_posts(posts):
    try:
        body = {'title':posts['title'], 'link':posts['link'],  'message':posts['message'], 'comments':posts['comments'], 'download_photos':posts['download_photos'], 
        'photos':posts['photos'], 'category':posts['category']}
        response = restclient.helpbuys.create(body=body, params={}, headers={})
        print(response.status_code)
        if response.status_code == 201:
            print( 'insert ok')
    except:
        print("Unexpected error:", sys.exc_info()[0])


def set_collection(dst):
    global collection
    collection = dst
def insert_posts(posts):
    client = MongoClient('mongodb://localhost:27017/luxurai_backend?authSource=admin', username='db_agent', password='Ie!5Og@rHPAe')
    with client:
        try:
            db = client['luxurai_backend']

            db[collection].find_one_and_update({'link': posts['link']}, {"$set": dict(posts)}, upsert=True)
        except:
            print("Unexpected error:", sys.exc_info()[0])


def get_posts(db = 'luxurai_backend'):
    try:
        client = MongoClient('mongodb://localhost:27017/luxurai_backend?authSource=admin', username='db_agent', password='Ie!5Og@rHPAe')
        with client:
        
            record = list(client[db][collection].aggregate([{"$sort":{"time":-1}}, {"$limit":1}]))
            if len(record) == 0:
                return None
            locale.setlocale(locale.LC_ALL, 'zh_CN.utf-8')
            return time.strptime(record[0]['time'], '%Y年%m月%d日 %A%p%I:%M')
            #last_time = record[0]
            #for doc in record:
            #    print(doc)
    except:
        print('unexpected error:', sys.exc_info()[0])
