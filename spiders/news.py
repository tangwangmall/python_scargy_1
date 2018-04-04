import scrapy
from items import ContentItem


class NewsSpider(scrapy.Spider):
    name = 'news'
    host = 'http://jiangsu.chinaccs.cn/'
    domain = 'http://jiangsu.chinaccs.cn/News.aspx'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "jiangsu.chinaccs.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }

    def __init__(self, url=None):
        self.user_url = url

    def start_requests(self):
        yield scrapy.Request(
            url=self.domain,
            headers=self.headers,
            callback=self.request_body
        )

    def request_body(self, response):
        def value(list1):
            return list1[0] if len(list1) else ''

        sel = response.xpath('//div[@class="slideTxtBox3"]//li')
        items = []
        for site in sel:
            item = ContentItem()
            detail_url = value(site.xpath('./a/@href').extract())
            publish_date_label = site.xpath('./a/label')
            publish_date = value(publish_date_label[1].xpath('./text()').extract())
            get_url = self.host + detail_url
            item['url'] = get_url
            item['publish_date'] = publish_date
            print(detail_url)
            items.append(item)

        for item in items:
            yield scrapy.Request(
                url=item['url'],
                meta={'item': item},
                headers=self.headers,
                callback=self.request_detail
            )

    def request_detail(self, response):
        def value(list1):
            return list1[0] if len(list1) else ''

        item = response.meta['item']
        sel = response.xpath('//div[@class="box01 boxForNews"]')
        title = value(sel.xpath('./h1/text()').extract())

        labels = sel.xpath('./div[@class="jianjie"]/label')
        publish_company = ''
        author = ''
        publish_date = ''
        if len(labels) >= 3:
            publish_company = value(labels[0].xpath('./text()').extract()).strip().strip("\r\n").strip("\r").split("\n")
            author = value(labels[1].xpath('./text()').extract()).strip().strip("\r\n").strip("\r").split("\n")
            publish_date = value(labels[2].xpath('./text()').extract()).strip().strip("\r\n").strip("\r").split("\n")
            print(publish_company)
            print(author)
            print(publish_date)
        print(title)
        imgs = sel.xpath('./div[@class="newsbox02"]/span//img')
        img_urls = []
        for im in imgs:
            img_src = value(im.xpath("./@src")).extract()
            img_urls.append(img_src)
        content = value(sel.xpath('./div[@class="newsbox02"]/span')).extract()
        print('-----------------------' + content)
        item['title'] = title
        item['img_urls'] = img_urls
        item['author'] = author[0]
        item['publish_company'] = publish_company[0]
        # item['publish_date'] = publish_date[0]
        item['content'] = content
        yield item
