from scrapy import cmdline

cmdline.execute("scrapy crawl news -a url=http://jiangsu.chinaccs.cn/News.aspx".split())