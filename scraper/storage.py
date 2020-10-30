from pymongo import MongoClient
import sys
import time
import locale
import datetime
from simple_rest_client.api import API
from simple_rest_client.resource import Resource
from bson.objectid import ObjectId

local_dbaddr = 'localhost'
remote_dbaddr = '52.194.223.156'
db_username = 'db_agent'
db_passwd = 'Ie!5Og@rHPAe'
db_authsource = 'admin'
db_authMechanism = 'SCRAM-SHA-256'
current_dbaddr = remote_dbaddr
class HelpbuysResource(Resource):
    actions = {
        "retrieve_latest": {"method": "GET", "url": "helpbuys?%24limit=1&$sort[time]=-1"},
        "retrieve": {"method": "GET", "url": "users/{}"},
        "retrieve_media": {"method": "GET", "url": "users/{}/media/recent"},
        "retrieve_likes": {"method": "GET", "url": "users/self/media/recent"},
        "create": {"method": "POST", "url": 'helpbuys'},
    }

restclient = API(
    api_root_url='https://botadmin.luxurai.com/',
    #api_root_url='http://localhost:3030/',
    params={},
    headers={},
    timeout=2,
    append_slash=False,
    json_encode_body=True,
)
restclient.add_resource(resource_name='helpbuys', resource_class=HelpbuysResource)
collection = 'test'

def rest_insert_posts(posts):
    try:
        body = {'title':posts['title'], 'link':posts['link'],  'message':posts['message'], 'comments':posts['comments'], 'download_photos':posts['download_photos'], 
        'photos':posts['photos'], 'category':posts['category'], 'time':posts['time']}
        response = restclient.helpbuys.create(body=body, params={}, headers={})
        print(response.status_code)
        if response.status_code == 201:
            print( 'insert ok')
    except:
        print("rest_insert_posts Unexpected error:", sys.exc_info())


def set_collection(dst):
    global collection
    collection = dst


def update_user(user):
    client = MongoClient(current_dbaddr,
    username='db_agent',
    password='Ie!5Og@rHPAe',
    authSource='admin',
    authMechanism='SCRAM-SHA-256')
    #print('in update user')
    #print(client)
    with client:
        timenow = datetime.datetime.now()
        try:
            db = client['luxurai_backend'] 
            if db['fb_users'].find({'user_id': user['user_id']}).count()==0:
                #print('insert')
                user['createdAt']=timenow
                user['updatedAt']=timenow
                db['fb_users'].insert(user)
            else:
                #print('update')
                db['fb_users'].update_one(
                    {'user_id': user['user_id']},
                    {'$set':{
                        'updatedAt': timenow,
                        'group_ids': user['group_ids']
                    }}
                )
        except:
            print("Unexpected error:", sys.exc_info())
    pass
    
def update_post(posts):
    
    # client = MongoClient('mongodb://localhost:27017/luxurai_backend?authSource=admin', username='db_agent', password='Ie!5Og@rHPAe')
    client = MongoClient('52.194.223.156',
    username='db_agent',
    password='Ie!5Og@rHPAe',
    authSource='admin',
    authMechanism='SCRAM-SHA-256')
    print('in update post')
    print(client)
    with client:
        timenow = datetime.datetime.now()
        try:
            db = client['luxurai_backend'] 
            if db['helpbuys'].find({'post_id': posts['post_id']}).count()==0:
                print('insert')
                posts['createdAt']=timenow
                posts['updatedAt']=timenow
                db['helpbuys'].insert(posts)
            else:
                print('update')
                db['helpbuys'].update_one(
                    {'post_id': posts['post_id']},
                    {'$set':{
                        'updatedAt': timenow,
                        'comments': posts['comments'],
                        'interactions': posts['interactions']
                    }}
                )
        except:
            print("Unexpected error:", sys.exc_info())



def rest_get_posts(db = 'luxurai_backend'):
    try:
        response = restclient.helpbuys.retrieve_latest(body={}, params={}, headers={})
        print(response.body)
        if len(response.body['data']) == 0 or 'time' not in response.body['data'][0].keys():
            return None
        record = response.body['data']
        locale.setlocale(locale.LC_ALL, 'zh_CN.utf-8')
        return time.strptime(record[0]['time'], '%Y年%m月%d日 %A%p%I:%M')
    except:
        print('unexpected error:', sys.exc_info())

def get_posts(db = 'luxurai_backend'):
    try:
        client = MongoClient('52.194.223.156',
        username='db_agent',
        password='Ie!5Og@rHPAe',
        authSource='admin',
        authMechanism='SCRAM-SHA-256')      
        with client:
        
            record = list(client[db][collection].aggregate([{"$sort":{"time":-1}}, {"$limit":1}]))
            if len(record) == 0:
                return None
            locale.setlocale(locale.LC_ALL, 'zh_CN.utf-8')
            return time.strptime(record[0]['updatedAt'], '%Y年%m月%d日 %A%p%I:%M')
            #last_time = record[0]
            #for doc in record:
            #    print(doc)
    except:
        print('unexpected error:', sys.exc_info())

def get_post(post_id, db = 'luxurai_backend'):

    post = {}

    if post_id == '':
        return []
    
    try:
        client = MongoClient('52.194.223.156',
        username='db_agent',
        password='Ie!5Og@rHPAe',
        authSource='admin',
        authMechanism='SCRAM-SHA-256')      
        with client:
            db = client['luxurai_backend']
            post = db['helpbuys'].find_one({'post_id': post_id})            
        
    except:
        print('unexpected error:', sys.exc_info())

    return post

def get_fbuser(user_id, db = 'luxurai_backend'):

    user = {}

    if user_id == '':
        return []
    
    try:
        client = MongoClient(current_dbaddr,
        username=db_username,
        password=db_passwd,
        authSource=db_authsource,
        authMechanism=db_authMechanism)      
        with client:
            db = client['luxurai_backend']
            user = db['fb_users'].find_one({'user_id': user_id})            
        
    except:
        print('unexpected error:', sys.exc_info())

    return user

