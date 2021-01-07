#!/usr/bin/python3
import datetime

import pymongo

def get_cookies():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["cookies"]["weibo"]

    x = list(db.aggregate([{ '$sample': { 'size': 1 } }]))
    cookiedict = {}
    # print(x)
    for item in x[0]["cookie"]["cookie"]:
        y = item.split('=')
        cookiedict[y[0]] = y[1]
    return cookiedict,x[0]

def delete_cookies(cookie):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["cookies"]["weibo"]
    db2 = myclient["cookies"]["fail"]

    # search = []
    # for i in cookie:
    #     vari = '%s=%s' % (i, cookie[i])
    #     search.append(vari)
    userid = cookie['cookie']['uinfo']['uid']

    delete_data = db.find_one({'cookie.uinfo.uid':userid})
    if int(delete_data['cookie']['uinfo']['fail_count']) < 10 :
        db.update({'cookie.uinfo.uid': delete_data['cookie']['uinfo']['uid']},{ '$set': {'cookie.uinfo.fail_count': int(int(delete_data['cookie']['uinfo']['fail_count'])+1)}})
        print('ID : %s  Fail : %s'%(str(delete_data['cookie']['uinfo']['uid']),str(delete_data['cookie']['uinfo']['fail_count'])))
    else:
        delete_data['cookie']['uinfo']['fail_count'] = 10
        delete_data['cookie']['uinfo']['remove_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db2.insert_one(delete_data)
        db.delete_one({'cookie.uinfo.uid': delete_data['cookie']['uinfo']['uid']})
    return delete_data