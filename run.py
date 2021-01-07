from scrapy import cmdline
from CheckCookies import CheckCookies
from DownLoadImg import downloadimg
from Format_data import d2j

uid = '5533039912'
pathname = './Draw'
dbname = 'weibo12'
check = CheckCookies(dbname).main()

cmdline.execute(['scrapy', 'crawl', 'weibo'])

di = downloadimg(dbname,dic_path = pathname+'/img')
di.run()
di.replace_img()
jsonpath = pathname+'/data.json'
dj = d2j(dbname, jsonpath,uid)
dj.main()