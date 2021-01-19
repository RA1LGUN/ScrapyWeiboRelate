# ScrapyWeiboRelate

通过Scrapy爬取微博数据并通过AntV绘制出人际关系网络图<br>
![GitHub license](https://badgen.net/github/license/HUANGZHIHAO1994/weibo-analysis-and-visualization?color=green)
![python](https://badgen.net/badge/python/%3E=3.6/8d6fe7)
- en [English](/README_EN.md)

## 项目说明

### 爬虫功能
1. 爬取微博用户信息

2. 用户近期微博

3. 用户社交关系抓取(粉丝/关注)

### 如何使用
1. 修改spiders/weibo.py中的 user_id = int('用户ID') ，确定以哪一位用户为核心发散关系
2. 修改relate_deep = 2与deepth_fans = 2，确定发散深度（deepth为2则包括我的关注/粉丝的关注/粉丝，数量指数倍增长）
3. 请重写proxy_handle与get_cookies，确保middlewares能获得正确的cookie及IP代理
4. 运行run.py
5. 打开Draw/index.html,重要参数有：linkDistance: 50（控制边长）,endArrow: true（边是否有箭头）,lineWidth: 0.65（边的粗细）,可根据需要自行更改

### 特别注意
1. 因为我的cookie池规模太小，故在spiders/weibo.py的73行,107行,132行,166行,258行加了time.sleep,运行速度慢非其他原因
2. 爬取时对用户进行了筛选，过滤掉了大V和粉丝数大于10000的用户
3. 训练语料不足导致NLP的准确率为89%,故本项目附训练语料（语料出处不详，于CDSN下载）

### 最后效果
1. 1000个节点左右
![800](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115811.png)
![1000+](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115809.png)

2. 5000个节点左右
![4800](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115802.png)

3. 10000+个节点
![14000](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115817.png)

4. 粉丝及关注用不同颜色的线区分
![1000](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/muti_color.png)
![1000](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/5000color.png)


## 完成进度
现主要功能都已开发完成,正在优化图像可读性及其他小工具，并将友善度和社交关系相关联

## 感谢

感谢对我的帮助及指导

<img src="http://qlogo1.store.qq.com/qzone/1845370492/1845370492/100?1570026854" title="Code">

## 说明

因为微博反爬能力增强，项目中的模拟登陆功能已失效，关注/粉丝也只能爬到前20页，但是这部分本项目不再做更新，重点展示用户之间的关系，特此说明。
