import scrapy
from nycopendata_scrape.items import DatasetItem
from datetime import datetime as dt
import re
import json

def custom_strip_tags(string):
    '''
    takes and returns a string.
    strips out: h1, h2, h3, span, img, p, a, div, comments,
    plus .strip()
    leaves: ul, li, strong, em
    '''
    string = re.sub(r'<h1[^>]*>', '', string)
    string = re.sub(r'</h1>', '', string)
    string = re.sub(r'<h2[^>]*>', '', string)
    string = re.sub(r'</h2>', '', string)
    string = re.sub(r'<h3[^>]*>', '', string)
    string = re.sub(r'</h3>', '', string)
    string = re.sub(r'<span[^>]*>', '', string)
    string = re.sub(r'</span>', '', string)
    string = re.sub(r'<section[^>]*>', '', string)
    string = re.sub(r'</section>', '', string)
    string = re.sub(r'<p[^>]*>', '', string)
    string = re.sub(r'</p>', '', string)
    string = re.sub(r'<img[^>]*>', '', string)
    string = re.sub(r'<a[^>]*>', '', string)
    string = re.sub(r'</a>', '', string)
    string = re.sub(r'<div[^>]*>', '', string)
    string = re.sub(r'</div>', '', string)
    string = re.sub(r'<br[^>]*>', '', string)
    string = re.sub(r'<source[^>]*>', '', string, flags=re.DOTALL)
    string = re.sub(r'<meta[^>]*>', '', string)
    string = re.sub(r'<style>.*</style>', '', string, flags=re.DOTALL)
    string = re.sub(r'<form.*</form>', '', string, flags=re.DOTALL)
    string = re.sub(r'<!--[^>]*>', '', string).strip()
    return string

class NycopendataSpider(scrapy.Spider):
    name = "nycopendata"
    allowed_domains = ["data.cityofnewyork.us"]
    start_urls = ["https://data.cityofnewyork.us/browse?page=1"]
    page_number = 1

    def parse(self, response):
        results = response.xpath("//div[@class='browse2-result']")
        if results:
            for result in results:
                item = DatasetItem()
                item['name'] = result.xpath(".//a[@class='browse2-result-name-link']/text()").get()
                item['url'] = result.xpath(".//a[@class='browse2-result-name-link']/@href").get()
                item['id'] = re.search(r"[^/]+$", item['url']).group(0)
                item['api_url'] = f'https://data.cityofnewyork.us/resource/{item['id']}.json'
                if result.xpath(".//div[@class='browse2-result-description-container']/div/div/div").get():
                    item['description'] = custom_strip_tags(result.xpath(".//div[@class='browse2-result-description-container']/div/div/div").get())
                item['category'] = result.xpath(".//a[contains(@class, 'browse2-result-category')]/text()").get()
                item['updated'] = dt.strptime(result.xpath(".//span[@class='dateLocalize']/text()").get(), '%B %d %Y').date()
                item['views'] = int(re.sub(r'\D', '', result.xpath(".//div[@class='browse2-result-view-count-value']/text()").get().strip()))
                item['data_type'] = result.xpath(".//span[@class='browse2-result-type-name']/text()").get()

                yield scrapy.Request(response.urljoin(item['url']), callback=self.parse_data_page, meta={'item': item,})
            
            self.page_number += 1
            next_page = re.sub(r'\d+$', '', response.url) + str(self.page_number)
            yield response.follow(next_page, self.parse)

    
    def parse_data_page(self, response):
        item = response.meta['item']
        # item['description'] = response.xpath("//meta[@name='description']/@content").get()
        s = response.xpath("//script").getall()[-3]
        data = re.search(r'var\s+initialState\s*=\s*(\{.*\})', s.strip(), re.DOTALL)
        if data:
            data_json = json.loads(data.group(1))
            if data_json.get('view'):
                if data_json['view'].get('columns'):
                    if len(data_json['view']['columns']) > 0:
                        if data_json['view']['columns'][0].get('cachedContents'):
                            if data_json['view']['columns'][0]['cachedContents'].get('count'):
                                item['rows'] = int(data_json['view']['columns'][0]['cachedContents']['count'])
                        elif data_json['view']['columns'][1].get('cachedContents'):
                            if data_json['view']['columns'][0]['cachedContents'].get('count'):
                                item['rows'] = int(data_json['view']['columns'][0]['cachedContents']['count'])
                        elif data_json['view']['columns'][2].get('cachedContents'):
                            if data_json['view']['columns'][0]['cachedContents'].get('count'):
                                item['rows'] = int(data_json['view']['columns'][0]['cachedContents']['count'])
        yield item



    