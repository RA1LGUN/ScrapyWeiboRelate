import json
import re

import pymongo
import copy


class d2j():

    def __init__(self, dbname, path, uid):
        self.to_json_dic = {}
        self.collection = pymongo.MongoClient("mongodb://localhost:27017/")[dbname]['user']
        self.collection2 = pymongo.MongoClient("mongodb://localhost:27017/")[dbname]['relate']
        self.list1 = []
        self.nodelist = []
        self.list2 = []
        self.edgeslist = []
        self.filename = path
        self.uid = uid
        self.user = {self.uid: [{}]}
        self.follower = {self.uid: [{}]}
        self.user_follower = None
        self.follower_user = None

    def main(self):

        self.get_nodes()
        self.get_dataStructure()
        self.get_edges()

        self.to_json_dic['nodes'] = self.nodelist
        self.to_json_dic['edges'] = self.edgeslist

        with open(self.filename, 'w', encoding='utf-8') as file_obj:
            json.dump(self.to_json_dic, file_obj)
            print(self.to_json_dic)

    def str_label(self, item):
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

    def img_path(self, img_item):
        img_localpath = './img/%s.%s'
        if bool(re.findall(r'[0-9]{3}/(.+.jpg)', img_item['src_url'])):
            jpgname = img_item['src_url'][-10:]
            jpgname = jpgname.replace('%', 'PC')
            # print(jpgname)
            jpg_path = img_localpath % (jpgname, 'jpg')
            return jpg_path
        elif bool(re.findall(r'/images/(.+.gif)', img_item['src_url'])):
            gifname = img_item['src_url'][-10:]
            gifname = gifname.replace('%', 'PC')
            gif_path = img_localpath % (gifname, 'gif')
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
                    folnum = list(self.collection2.find({'followuser': item['id']}).sort("deepth", 1))[0]['deepth']
                except:
                    folnum = 10
                try:
                    fannum = list(self.collection2.find({'userid': item['id']}).sort("deepth", 1))[0]['deepth']
                except:
                    folnum = 10

                if folnum > fannum:
                    clsnum = fannum
                elif folnum < fannum:
                    clsnum = folnum + 3
                else:
                    clsnum = fannum

            vardict['class'] = str(clsnum)

            self.nodelist.append(vardict)

    def frendly(self):
        pass


    def get_dataStructure(self):
        for l in self.collection2.find():
            if str(l["userid"]) == self.uid:
                self.user[self.uid][0][str(l["followuser"])] = [{}]

            if str(l["followuser"]) == self.uid:
                self.follower[self.uid][0][str(l["userid"])] = [{}]

        self.user_follower = copy.deepcopy(self.user)
        self.follower_user = copy.deepcopy(self.follower)

        for l in self.collection2.find():
            for u in list(self.user[self.uid][0].keys()):
                if str(l["userid"]) == u and str(l["followuser"]) != self.uid:
                    self.user[self.uid][0][u][0][str(l["followuser"])] = [{}]

        for l in self.collection2.find():
            for u in list(self.follower[self.uid][0].keys()):
                if str(l["followuser"]) == u and str(l["userid"]) != self.uid:
                    self.follower[self.uid][0][u][0][str(l["userid"])] = [{}]

        for l in self.collection2.find():
            for u in list(self.follower[self.uid][0].keys()):
                if str(l["userid"]) == u and str(l["followuser"]) != self.uid:
                    self.follower_user[self.uid][0][u][0][str(l["followuser"])] = [{}]

        for l in self.collection2.find():
            for u in list(self.user[self.uid][0].keys()):
                if str(l["followuser"]) == u and str(l["userid"]) != self.uid:
                    self.user_follower[self.uid][0][u][0][str(l["userid"])] = [{}]

    def get_edges(self):

        # handle user edge
        user_target = list(self.user.keys())
        user_source = list(list(self.user.values())[0][0].keys())
        for source in user_source:
            edgesvardict = {}
            edgesvardict['source'] = source
            edgesvardict['target'] = user_target[0]
            edgesvardict['value'] = str(1)
            edgesvardict['lineWidth'] = str(6 - int(1 * 1.5))
            edgesvardict['color'] = '#8B0000'
            self.edgeslist.append(edgesvardict)
            self.list2.append(int(user_target[0]))
            self.list2.append(int(source))

        user_target = copy.deepcopy(user_source)
        for target in user_target:
            user_source = list(self.user[self.uid][0][target][0].keys())
            for source in user_source:
                edgesvardict = {}
                edgesvardict['source'] = source
                edgesvardict['target'] = target
                edgesvardict['value'] = str(1)
                edgesvardict['lineWidth'] = str(6 - int(2 * 1.5))
                edgesvardict['color'] = '#FF0000'
                self.edgeslist.append(edgesvardict)
                self.list2.append(int(target))
                self.list2.append(int(source))

        # handle follower edges
        follower_source = list(self.follower.keys())
        follower_target = list(list(self.follower.values())[0][0].keys())
        for target in follower_target:
            edgesvardict = {}
            edgesvardict['source'] = follower_source[0]
            edgesvardict['target'] = target
            edgesvardict['value'] = str(1)
            edgesvardict['lineWidth'] = str(6 - 1 * 1.5)
            edgesvardict['color'] = '#00008B'
            self.edgeslist.append(edgesvardict)
            self.list2.append(int(target))
            self.list2.append(int(follower_source[0]))

        follower_source = copy.deepcopy(follower_target)
        for source in follower_source:
            follower_target = list(self.follower[self.uid][0][source][0].keys())
            for target in follower_target:
                edgesvardict = {}
                edgesvardict['source'] = source
                edgesvardict['target'] = target
                edgesvardict['value'] = str(1)
                edgesvardict['lineWidth'] = str(6 - 2 * 1.5)
                edgesvardict['color'] = '#0000FF'
                self.edgeslist.append(edgesvardict)
                self.list2.append(int(target))
                self.list2.append(int(source))

        follower_user_target = list(list(self.follower_user.values())[0][0].keys())
        for target in follower_user_target:
            follower_user_source = list(self.follower_user[self.uid][0][target][0].keys())
            for source in follower_user_source:
                edgesvardict = {}
                edgesvardict['source'] = source
                edgesvardict['target'] = target
                edgesvardict['value'] = str(1)
                edgesvardict['lineWidth'] = str(6 - 2 * 1.5)
                edgesvardict['color'] = '#FF0000'
                self.edgeslist.append(edgesvardict)
                self.list2.append(int(target))
                self.list2.append(int(source))

        user_follower_source = list(list(self.user_follower.values())[0][0].keys())
        for source in user_follower_source:
            user_follower_target = list(self.user_follower[self.uid][0][source][0].keys())
            for target in user_follower_target:
                edgesvardict = {}
                edgesvardict['source'] = source
                edgesvardict['target'] = target
                edgesvardict['value'] = str(1)
                edgesvardict['lineWidth'] = str(6 - 2 * 1.5)
                edgesvardict['color'] = '#0000FF'
                self.edgeslist.append(edgesvardict)
                self.list2.append(int(target))
                self.list2.append(int(source))

        list1 = list(set(self.list1))
        except_list = list(set(self.list2).difference(set(list1)))

        for noneuser in except_list:
            vardict2 = {}
            vardict2['id'] = str(noneuser)
            vardict2['img'] = "./img/kqbMa6HGNF.gif"
            jsonstr = '出了一些小小的问题'
            vardict2['label'] = json.dumps(jsonstr)
            self.nodelist.append(vardict2)


if __name__ == '__main__':
    pathname = 'data.json'
    dbname = 'weibo9'
    uid = '3746520465'
    d2j(dbname, pathname, uid).main()
