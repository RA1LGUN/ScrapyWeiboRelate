import json
import re

import pymongo

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
        # self.get_edges()
        self.color_edges()
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
            try:
                labeldict['gender'] = item['gender']
            except:
                pass
            try:
                labeldict['province'] = item['province']
            except:
                pass
            try:
                labeldict['labels'] = item['labels']
            except:
                pass
            try:
                labeldict['city'] = item['city']
            except:
                pass
            try:
                labeldict['vip_level'] = item['vip_level']
            except:
                pass
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

            vardict['class'] = str(clsnum)

            self.nodelist.append(vardict)

    def frendly(self):
        pass



    # def get_color(self,item):
    #
    #     if item['userid'] == '6056282307':
    #         linecolor = '#FF6A6A'
    #     else:
    #         linecolor = '#436EEE'
    #
    #     return linecolor

    def color_edges(self):
        firfo = list(self.collection2.find({'followuser':self.uid}))
        while firfo:                #第一层，从userid开始发散
            for firfollow in firfo:

                secfo = list(self.collection2.find({'followuser':firfollow['userid']}))
                while secfo:        #第二层，关注
                    for secfollow in secfo:

                        secfofa = list(self.collection2.find({'userid':secfollow['userid']}))
                        while secfofa:  #第三层 粉丝
                            for thifan in secfofa:
                                edgesvardict = {}
                                edgesvardict['source'] = str(thifan['userid'])
                                edgesvardict['target'] = str(thifan['followuser'])
                                # edgesvardict['label'] = str(item2['deepth'])
                                edgesvardict['value'] = str(thifan['weight'] + 1)
                                edgesvardict['lineWidth'] = str(6 - int(thifan['deepth'] * 1.5))
                                edgesvardict['color'] = str('#7975E7')
                                self.edgeslist.append(edgesvardict)
                            secfofa = []

                        secfofo = list(self.collection2.find({'followuser':secfollow['userid']}))
                        while secfofo:  #第三层  关注
                            for thirfo in secfofo:
                                edgesvardict = {}
                                edgesvardict['source'] = str(thirfo['userid'])
                                edgesvardict['target'] = str(thirfo['followuser'])
                                # edgesvardict['label'] = str(item2['deepth'])
                                edgesvardict['value'] = str(thirfo['weight'] + 1)
                                edgesvardict['lineWidth'] = str(6 - int(thirfo['deepth'] * 1.5))
                                edgesvardict['color'] = str('#0F3057')
                                self.edgeslist.append(edgesvardict)
                            secfofo = []
                        edgesvardict = {}
                        edgesvardict['source'] = str(secfollow['userid'])
                        edgesvardict['target'] = str(secfollow['followuser'])
                        # edgesvardict['label'] = str(item2['deepth'])
                        edgesvardict['value'] = str(secfollow['weight'] + 1)
                        edgesvardict['lineWidth'] = str(6 - int(secfollow['deepth'] * 1.5))
                        edgesvardict['color'] = str('#00587A')
                        self.edgeslist.append(edgesvardict)
                    secfo = []


                secfa = list(self.collection2.find({'userid':firfollow['userid']}))
                while secfa:        #第二层 粉丝
                    for secfan in secfa:
                        secfafa = list(self.collection2.find({'userid': secfan['followuser']}))

                        while secfafa:      #第三层 粉丝
                            for thifan in secfafa:
                                edgesvardict = {}
                                edgesvardict['source'] = str(thifan['userid'])
                                edgesvardict['target'] = str(thifan['followuser'])
                                # edgesvardict['label'] = str(item2['deepth'])
                                edgesvardict['value'] = str(thifan['weight'] + 1)
                                edgesvardict['lineWidth'] = str(6 - int(thifan['deepth'] * 1.5))
                                edgesvardict['color'] = str('#008891')
                                self.edgeslist.append(edgesvardict)
                            secfafa = []

                        secfafo = list(self.collection2.find({'followuser': secfan['followuser']}))
                        while secfafo:      #第三层 关注
                            for thifo in secfafo:
                                edgesvardict = {}
                                edgesvardict['source'] = str(thifo['userid'])
                                edgesvardict['target'] = str(thifo['followuser'])
                                # edgesvardict['label'] = str(item2['deepth'])
                                edgesvardict['value'] = str(thifo['weight'] + 1)
                                edgesvardict['lineWidth'] = str(6 - int(thifo['deepth'] * 1.5))
                                edgesvardict['color'] = str('#9AB3F5')
                                self.edgeslist.append(edgesvardict)
                            secfafo = []
                        edgesvardict = {}
                        edgesvardict['source'] = str(secfan['userid'])
                        edgesvardict['target'] = str(secfan['followuser'])
                        # edgesvardict['label'] = str(item2['deepth'])
                        edgesvardict['value'] = str(secfan['weight'] + 1)
                        edgesvardict['lineWidth'] = str(6 - int(secfan['deepth'] * 1.5))
                        edgesvardict['color'] = str('#A3D8F4')
                        self.edgeslist.append(edgesvardict)
                    secfa = []
            firfo = []

        firfa = list(self.collection2.find({'userid': self.uid}))
        while firfa:  # 第一层，从userid开始发散
            for firfallow in firfa:

                sec_fo = list(self.collection2.find({'followuser': firfallow['followuser']}))
                while sec_fo:  # 第二层，关注
                    for sec_follow in sec_fo:

                        sec_fofa = list(self.collection2.find({'userid': sec_follow['userid']}))
                        while sec_fofa: #第三层 粉丝
                            for thifan in sec_fofa:
                                edgesvardict = {}
                                edgesvardict['source'] = str(thifan['userid'])
                                edgesvardict['target'] = str(thifan['followuser'])
                                # edgesvardict['label'] = str(item2['deepth'])
                                edgesvardict['value'] = str(thifan['weight'] + 1)
                                edgesvardict['lineWidth'] = str(6 - int(thifan['deepth'] * 1.5))
                                edgesvardict['color'] = str('#FF414D')
                                self.edgeslist.append(edgesvardict)
                            sec_fofa = []

                        sec_fofo = list(self.collection2.find({'followuser': sec_follow['followuser']}))
                        while sec_fofo: #第三层 关注
                            for thirfo in sec_fofo:
                                edgesvardict = {}
                                edgesvardict['source'] = str(thirfo['userid'])
                                edgesvardict['target'] = str(thirfo['followuser'])
                                # edgesvardict['label'] = str(item2['deepth'])
                                edgesvardict['value'] = str(thirfo['weight'] + 1)
                                edgesvardict['lineWidth'] = str(6 - int(thirfo['deepth'] * 1.5))
                                edgesvardict['color'] = str('#F56A79')
                                self.edgeslist.append(edgesvardict)
                            sec_fofo = []
                        edgesvardict = {}
                        edgesvardict['source'] = str(sec_follow['userid'])
                        edgesvardict['target'] = str(sec_follow['followuser'])
                        # edgesvardict['label'] = str(item2['deepth'])
                        edgesvardict['value'] = str(sec_follow['weight'] + 1)
                        edgesvardict['lineWidth'] = str(6 - int(sec_follow['deepth'] * 1.5))
                        edgesvardict['color'] = str('#DE4463')
                        self.edgeslist.append(edgesvardict)
                    sec_fo = []

                sec_fa = list(self.collection2.find({'userid': firfallow['followuser']}))
                while sec_fa:   #第二层 粉丝
                    for sec_fan in sec_fa:
                        sec_fafa = list(self.collection2.find({'userid': sec_fan['followuser']}))

                        while sec_fafa: #第三层 关注
                            for thifan in sec_fafa:
                                edgesvardict = {}
                                edgesvardict['source'] = str(thifan['userid'])
                                edgesvardict['target'] = str(thifan['followuser'])
                                # edgesvardict['label'] = str(item2['deepth'])
                                edgesvardict['value'] = str(thifan['weight'] + 1)
                                edgesvardict['lineWidth'] = str(6 - int(thifan['deepth'] * 1.5))
                                edgesvardict['color'] = str('#D789D7')
                                self.edgeslist.append(edgesvardict)
                            sec_fafa = []

                        sec_fafo = list(self.collection2.find({'followuser': sec_fan['userid']}))
                        while sec_fafo: #第三层 粉丝
                            for thirfo in sec_fafo:
                                edgesvardict = {}
                                edgesvardict['source'] = str(thirfo['userid'])
                                edgesvardict['target'] = str(thirfo['followuser'])
                                # edgesvardict['label'] = str(item2['deepth'])
                                edgesvardict['value'] = str(thirfo['weight'] + 1)
                                edgesvardict['lineWidth'] = str(6 - int(thirfo['deepth'] * 1.5))
                                edgesvardict['color'] = str('#9D6579')
                                self.edgeslist.append(edgesvardict)
                            sec_fafo = []
                        edgesvardict = {}
                        edgesvardict['source'] = str(sec_fan['userid'])
                        edgesvardict['target'] = str(sec_fan['followuser'])
                        # edgesvardict['label'] = str(item2['deepth'])
                        edgesvardict['value'] = str(sec_fan['weight'] + 1)
                        edgesvardict['lineWidth'] = str(6 - int(sec_fan['deepth'] * 1.5))
                        edgesvardict['color'] = str('#5D54A4')
                        self.edgeslist.append(edgesvardict)
                    sec_fa = []
            firfa = []

    def get_edges(self):
        for item2 in self.collection2.find():
            # edgesvardict ={}
            # edgesvardict['source'] = str(item2['userid'])
            # edgesvardict['target'] = str(item2['followuser'])
            # # edgesvardict['label'] = str(item2['deepth'])
            # edgesvardict['value'] = str(item2['weight']+1)
            # edgesvardict['lineWidth'] = str(6 - int(item2['deepth'] * 1.5))
            # edgesvardict['color'] = str(self.get_color(item2))
            # self.edgeslist.append(edgesvardict)
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


if __name__ == '__main__':
    pathname = 'data3.json'
    dbname = 'weibo10'
    uid = '6056282307'
    d2j(dbname,pathname,uid).main()