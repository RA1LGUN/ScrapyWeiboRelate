from scrapy import cmdline
from CheckCookies import CheckCookies
from DownLoadImg import downloadimg
from Format_data import d2j

# uid = '3746520465'
# pathname = './Draw'
# dbname = 'weibo11'
# check = CheckCookies(dbname).main()

cmdline.execute(['scrapy', 'crawl', 'weibo'])

# di = downloadimg(dbname,pathname = pathname+'/img')
# di.run()
# di.replace_img()
# jsonpath = pathname+'/data.json'
# dj = d2j(dbname, jsonpath,uid)
# dj.main()