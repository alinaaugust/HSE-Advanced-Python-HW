import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urljoin
import re
import json
from items import SteamSpiderItem

queries = ['adventure', 'anime', 'simulation']


class SteamSpider(scrapy.Spider):
    name = 'SteamSpider'
    allowed_domains = ['store.steampowered.com']

    def start_requests(self):
        for query in queries:
            url = 'https://store.steampowered.com/search/' + query
            yield scrapy.Request(url=url, callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        game_link = response.xpath('//a[@data-search-page="1" or @data-search-page="2"]')
        for link in game_link:
            yield scrapy.Request(url=link.get('href').strip(), callback=self.parse_game_page)

    def parse_game_page(self, response):
        items = SteamSpiderItem()
        title = response.xpath('//div[contains(@class, "apphub_AppName")]/text()')[0]
        category = response.xpath('//div[contains(@class, "blockbg")]//text()')[3:-2:2]
        mark = response.xpath('//div[contains(@class, "summary_section")]//text()')[3]
        reviews_number = response.xpath('//div[contains(@class, "summary_section")]//text()')[5][1:-1]
        release = response.xpath('//div[contains(@class, "release_date")]//text()')[-2]
        developer = response.xpath('//div[contains(@id, "developers_list")]//text()')[1]
        windows = response.xpath('//div[contains(@data-os, "win")]')
        mac = response.xpath('//div[contains(@data-os, "mac")]')
        linux = response.xpath('//div[contains(@data-os, "linux")]')
        price = response.xpath('//div[contains(@class, "discount_final_price")]//text()')[0]
        tags = response.xpath('//a[contains(@class, "app_tag")]//text()')
        items['game_name'] = ''.join(title).strip()
        s = '/'
        for c in category:
            s += c + '/'
        items['game_category'] = s
        items['overall_mark'] = ''.join(mark).strip()
        items['all_reviews'] = ''.join(reviews_number).strip()
        items['game_release_date'] = ''.join(release).strip()
        items['game_developer'] = ''.join(developer).strip()
        if windows:
            items['game_platforms'] = 'Windows'
        if mac:
            items['game_platforms'] += ', MacOS'
        if linux:
            items['game_platforms'] += ', Linux'
        items['game_price'] = price
        items['game_tags'] = '/'.join(tags).replace('\r', '').replace('\n', '').replace('\t', '').strip()
        yield items
