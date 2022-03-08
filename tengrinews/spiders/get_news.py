import scrapy
import re
import json


class GetNewsSpider(scrapy.Spider):
    name = 'get_news'
    allowed_domains = ['tengrinews.kz', 'c.tn.kz']
    start_urls = ['https://tengrinews.kz/kazakhstan_news/page/1']

    def parse(self, response):
        for article in response.css('.tn-article-item'):
            article_title = article.css('.tn-article-title::text').get()
            if article_title is None:
                continue
            article_link = article.xpath('a/@href').extract()
            if len(article_link) != 0:
                yield scrapy.Request('http://tengrinews.kz' + str(article_link[0]), callback=self.parse_article_content)

    def parse_article_content(self, response):
        page_id = re.search('-\d+/', response.url).group(0)[1:-1]
        data = {
            "id": page_id,
            "type": "news",
            "lang": "ru",
            "sort": "best"
        }
        yield scrapy.Request(
            url='https://c.tn.kz/comments/get/list/',
            body=json.dumps(data),
            method='POST',
            headers={
                'Accept': 'application / json, text / plain, * / *',
                'Content-Type': 'application/json;charset=UTF-8'
            },
            callback=self.get_article_comments
        )

    def get_article_comments(self, response):
        data = json.loads(response.body)
        s = json.dumps(data, indent=4, sort_keys=True)
        #print(s)

        #print(data['list'][0]['name'])
        print(data['list'][0]['news_header'])
        for top_comment in data['list']:
            yield {
                "username" : top_comment['name'],
                "comment" : top_comment['text']
            }
            #for comment in top_comment['child']:
            #    print(comment['name'])
            #    print(comment['text'])
            #    print('\n')

        