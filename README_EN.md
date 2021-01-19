# ScrapyWeiboRelate

Crawl tweet data via Scrapy and map out a network of people via AntV<br>
![GitHub license](https://badgen.net/github/license/HUANGZHIHAO1994/weibo-analysis-and-visualization?color=green)
![python](https://badgen.net/badge/python/%3E=3.6/8d6fe7)

## Project description

### Crawler functions
1. crawl twitter user information

2. recent user tweets

3. crawl users' social connections (followers/followers)

### How to use
1. modify user_id = int('user_id') in spiders/weibo.py to determine which user is the core of the relationship
2. modify relate_deep = 2 and deepth_fans = 2 to determine the depth of dispersion (deepth of 2 will include my followers/fans of followers/fans, the number of exponential growth)
3. please rewrite proxy_handle and get_cookies to make sure middlewares can get the correct cookie and IP proxy
4. run run.py
5. open Draw/index.html, important parameters are: linkDistance: 50 (control edge length), endArrow: true (whether the edge has arrows), lineWidth: 0.65 (the thickness of the edge), can be changed according to your needs

### Special note
1. because the size of my cookie pool is too small, so in spiders/weibo.py 73 lines, 107 lines, 132 lines, 166 lines, 258 lines added time.sleep, running slow for no other reason
2. the crawl filtered the users, filtered out the big V and the users with more than 10000 followers
3. the accuracy rate of NLP is 89% due to the lack of training corpus, so the training corpus is attached to this project (the source of the corpus is unknown, download it from CDSN)

### Final results
1. 1000 nodes or so
![800](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115811.png)
![1000+](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115809.png)

2. 5000 nodes or so
![4800](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115802.png)

3. 10000+ nodes
![14000](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20210107115817.png)

4. Fans and followers are distinguished by different colored lines
![1000](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/muti_color.png)
![1000](https://github.com/RA1LGUN/ScrapyWeiboRelate/blob/master/Pic/5000color.png)


## Completion progress
The main features are now complete, we are optimizing the readability of the images and other widgets, and correlating friendliness with social connections.

## Thanks

Thanks for your help and guidance

<img src="http://qlogo1.store.qq.com/qzone/1845370492/1845370492/100?1570026854" title="Code">

## Description

Because of the enhanced anti-crawl capability of Weibo, the mock login function in the project is no longer available and the followers/fans can only crawl to the first 20 pages, but this part of the project is no longer updated to focus on showing the relationships between users, so here is a note.
