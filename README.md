# ScrapyWeiboRelate

通过Scrapy爬取微博数据并通过AntV绘制出人际关系网络图

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

### 特别注意
因为我的cookie池规模太小，故在spiders/weibo.py的73行,107行,132行,166行,258行加了time.sleep,运行速度慢非其他原因

### 最后效果
1. 1000个节点左右
![800](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115811.png)
![1000+](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115809.png)

2. 5000个节点左右
![4800](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115802.png)

3. 10000+个节点
![14000](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115817.png)
