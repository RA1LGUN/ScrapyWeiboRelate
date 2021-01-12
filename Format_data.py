import json
import re

import pymongo
from numpy import mean


class d2j():

    def __init__(self,dbname,path,uid):
        self.to_json_dic = {}
        self.collection = pymongo.MongoClient("mongodb://localhost:27017/")[dbname]['user']
        self.collection2 =  pymongo.MongoClient("mongodb://localhost:27017/")[dbname]['relate']
        self.list1 = []
        self.nodelist = []
        self.list2 = []
        self.edgeslist = []
        self.filename = path
        self.uid = uid

    def main(self):

        self.get_nodes()
        self.get_edges()

        self.to_json_dic['nodes'] = self.nodelist
        self.to_json_dic['edges'] = self.edgeslist

        with open(self.filename, 'w', encoding='utf-8') as file_obj:
            json.dump(self.to_json_dic, file_obj)
            print(self.to_json_dic)

    def str_label(self,item):
        strlable = ''
        try:
            strlable = 'nick_name : %s' % item['nick_name']
        except:
            pass
        strlable = strlable + ' gender : %s' % item['gender']
        strlable = strlable + ' province : %s' % item['province']
        try:
            strlable = strlable + ' city : %s' % item['city']
        except:
            pass
        strlable = strlable + ' vip_level : %s' % item['vip_level']
        try:
            strlable = strlable + ' tweets_num : %s' % item['tweets_num']

        except:
            pass
        try:
            strlable = strlable + ' follows_num : %s' % item['follows_num']
        except:
            pass
        try:
            strlable = strlable + ' fans_num : %s' % item['fans_num']
        except:
            pass
        return strlable

    def img_path(self,img_item):
        img_localpath = './img/%s.%s'
        if bool(re.findall(r'[0-9]{3}/(.+.jpg)', img_item['src_url'])):
            jpgname = img_item['src_url'][-10:]
            jpgname = jpgname.replace('%','PC')
            # print(jpgname)
            jpg_path =  img_localpath%(jpgname,'jpg')
            return jpg_path
        elif bool(re.findall(r'/images/(.+.gif)', img_item['src_url'])):
            gifname = img_item['src_url'][-10:]
            gifname = gifname.replace('%','PC')
            gif_path =  img_localpath%(gifname, 'gif')
            return gif_path

    def get_nodes(self):
        for item in self.collection.find():
            vardict = {}
            self.list1.append(int(item['id']))
            vardict['id'] = str(item['id'])
            vardict['img'] = self.img_path(item)

            labeldict = {}

            try:
                labeldict['nick_name'] = item['nick_name']
            except:
                labeldict['nick_name'] = item['id']
            labeldict['gender'] = item['gender']
            labeldict['province'] = item['province']
            try:
                labeldict['labels'] = item['labels']
            except:
                pass
            try:
                labeldict['city'] = item['city']
            except:
                pass
            labeldict['vip_level'] = item['vip_level']
            try:
                labeldict['tweets_num'] = item['tweets_num']
                labeldict['follows_num'] = item['follows_num']
                labeldict['fans_num'] = item['fans_num']
            except:
                pass

            vardict['label'] = json.dumps(labeldict)

            if item['id'] == str(self.uid):
                clsnum = 0
            else:
                try:
                    folnum = list(self.collection2.find({'followuser':item['id']}).sort("deepth",1))[0]['deepth']
                except:
                    folnum = 10
                try:
                    fannum = list(self.collection2.find({'userid':item['id']}).sort("deepth",1))[0]['deepth']
                except:
                    folnum = 10

                if folnum > fannum:
                    clsnum = fannum
                elif folnum < fannum:
                    clsnum = folnum + 3
                else:
                    clsnum = fannum

                try:
                    labeldict['friendly'] = item['friendly_score']
                except:
                    pass

                try:
                    avg_fans, ave_follow = self.frendly(item)
                    labeldict['avg_fans'] = avg_fans
                    labeldict['avg_follow'] = ave_follow
                    avg_fans = 0.5
                    ave_follow = 0.5
                except:
                    pass

            vardict['class'] = str(clsnum)

            self.nodelist.append(vardict)

    def frendly(self,item):
        avg_fans_score = []
        avg_follow_score = []
        x = list(self.collection2.aggregate([{'$match': {'userid': item['id']}},
                                   {
                                       '$lookup': {
                                           "from": "user",
                                           "localField": "followuser",
                                           "foreignField": "id",
                                           "as": "score"
                                       }}
                                   ]))
        y = list(self.collection2.aggregate([{'$match': {'followuser': item['id']}},
                                   {
                                       '$lookup': {
                                           "from": "user",
                                           "localField": "userid",
                                           "foreignField": "id",
                                           "as": "score"
                                       }}
                                   ]))
        for i1 in range(len(x)):
            i1 = i1 - 1
            avg_fans_score.append(x[i1]['score'][0]['friendly_score'])

        for i2 in range(len(y)):
            i2 = i2 - 1
            avg_follow_score.append(y[i2]['score'][0]['friendly_score'])

        if avg_fans_score:
            result1 = mean(avg_fans_score)
        if avg_follow_score:
            result2 = mean(avg_follow_score)

        return result1,result2



    def get_color(self,item):

        vari = item['deepth']
        if vari == 1:
            linecolor = '#FF6A6A'
        elif vari == 2:
            linecolor = '#9932CC'
        else:
            linecolor = '#436EEE'

        return linecolor

    def get_edges(self):
        for item2 in self.collection2.find():
            edgesvardict ={}
            edgesvardict['source'] = str(item2['userid'])
            edgesvardict['target'] = str(item2['followuser'])
            # edgesvardict['label'] = str(item2['deepth'])
            edgesvardict['value'] = str(item2['weight']+0.8)
            edgesvardict['lineWidth'] = str(6 - int(item2['deepth'] * 1.5))
            edgesvardict['color'] = str(self.get_color(item2))
            self.edgeslist.append(edgesvardict)
            self.list2.append(int(item2['userid']))
            self.list2.append(int(item2['followuser']))

        list1 = list(set(self.list1))
        except_list = list(set(self.list2).difference(set(list1)))

        for noneuser in except_list:
            vardict2 = {}
            vardict2['id'] = str(noneuser)
            vardict2['img'] = "./img/kqbMa6HGNF.gif"
            jsonstr = '出了一些小小的问题'
            vardict2['label'] = json.dumps(jsonstr)
            self.nodelist.append(vardict2)


# if __name__ == '__main__':
#     pathname = '../Test/1063/data.json'
#     dbname = 'weibo11'
#     uid = '3746520465'
#     d2j(dbname,pathname,uid).main()