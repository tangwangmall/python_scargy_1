# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import cx_Oracle
import datetime
import os
from myconfig import IMAGES_STORE
import requests


class MyfirstProjectPipeline(object):
    def __init__(self):
        host = "192.168.109.153"  # 数据库ip
        port = "1521"  # 端口
        sid = "dailyTest"  # 数据库名称
        # dsn = cx_Oracle.makedsn(host, port, sid)
        self.conn = cx_Oracle.connect("ccsjs/123456@192.168.109.153:1521/dailyTest")
        # self.conn = pymysql.connect(user=DbConfig['user'], passwd=DbConfig['passwd'], db=DbConfig['db'],
        #                             host=DbConfig['host'], charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()
        dir_path = '{}'.format(IMAGES_STORE)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    def process_item(self, item, spider):
        curTime = datetime.datetime.now()
        try:

            # 栏目ID
            channel_id = '137'
            user_id = '1'
            type_id = '1'
            model_id = '1'
            site_id = '2'
            # 状态(0:草稿;1:审核中;2:审核通过;3:回收站;4:投稿;5:归档)
            status = '0'
            # sort_date = datetime.datetime.strptime(item['publish_date'], '%Y/%m/%d')
            sort_date = '2018/4/1' #item['publish_date']
            publish_company = item['publish_company']
            author = item['author']
            title = item['title']
            content = item['content']
            img_urls = item['img_urls']
            # 把图片下载下来
            dir_path = '{}'.format(IMAGES_STORE)

            store_imgs_path = []
            type_img_dir = ''
            for img_url in img_urls:
                print(img_url)
                filename = img_url.split('/')
                filename = filename[len(filename)-1]
                type_img_dir = '/u/cms/zhongbo/spiders/'+filename
                img_path = '{}//{}'.format(dir_path, filename)
                with open(img_path, 'wb') as f:
                    req = requests.get(img_url)
                    f.write(req.content)

            sql_check = "SELECT count(1) FROM JC_CONTENT_EXT where title='%s'" % title
            self.cursor.execute(sql_check)
            result = self.cursor.fetchall()
            content_count = result[0][0]

            if (content_count == 0):
                seq_content = "SELECT S_JC_CONTENT.Nextval FROM DUAL"
                self.cursor.execute(seq_content)
                result = self.cursor.fetchall()
                content_id = result[0][0]

                sql_str = "INSERT INTO JC_CONTENT (CONTENT_ID,CHANNEL_ID,USER_ID,TYPE_ID,MODEL_ID,SITE_ID,SORT_DATE,STATUS) VALUES (%s,%s,%s,%s,%s,%s,to_date('%s','YYYY-MM-DD'),%s)" % (
                    content_id, channel_id, user_id, type_id, model_id, site_id, sort_date, status)

                self.cursor.execute(sql_str)

                sql_str = "INSERT INTO JC_CONTENT_CHANNEL (CHANNEL_ID,CONTENT_ID) VALUES ('%s','%s')" % (
                    channel_id, content_id)

                self.cursor.execute(sql_str)

                sql_str = "INSERT INTO JC_CONTENT_COUNT (CONTENT_ID) VALUES ('%s')" % (
                    content_id)

                self.cursor.execute(sql_str)

                sql_str = "INSERT INTO JC_CONTENT_CHECK (CONTENT_ID) VALUES ('%s')" % (
                    content_id)

                self.cursor.execute(sql_str)

                sql_str = "INSERT INTO JC_CONTENT_EXT (CONTENT_ID,TITLE,SHORT_TITLE,AUTHOR,ORIGIN,RELEASE_DATE,TYPE_IMG) VALUES ('%s','%s','%s','%s','%s',to_timestamp('%s','yyyy-mm-dd'),'%s')" % (
                    content_id, title, title, author, publish_company, sort_date,type_img_dir)

                self.cursor.execute(sql_str)

                sql_str = "INSERT INTO jc_content_txt (CONTENT_ID,TXT) VALUES ('%s',  :blobData)" % (
                    content_id)

                self.cursor.setinputsizes(blobData=cx_Oracle.CLOB)
                self.cursor.execute(sql_str, {'blobData': content})

                # sql_str = "INSERT INTO TW_CONTENT (TITLE,CONTENT) VALUES ('%s',  :blobData)" % (
                #     title)
                #
                # self.cursor.setinputsizes(blobData=cx_Oracle.BLOB)
                # self.cursor.execute(sql_str, {'blobData': content})
                self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            print('Error %d' % (err.args[0]))
        return item

    def close_spider(self, spider):
        if self.conn is not None:
            self.cursor.close()
            self.conn.close()
            self.conn = None
