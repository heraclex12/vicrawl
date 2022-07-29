from typing import Text, Dict, List, Any, Set
from bs4 import BeautifulSoup
import json
import re
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from base_selenium import BaseSeleniumCrawler


class VozCrawler(BaseSeleniumCrawler):
    base_url = 'https://voz.vn/'
    DELAY_TIME = 3

    def open_an_url(self, url: Text, browser: uc.Chrome):
        while True:
            try:
                browser.delete_all_cookies()
                browser.get(url)
                time.sleep(self.DELAY_TIME)
                break
            except Exception as e:
                browser.quit()
                browser = self.init_browser()
        return browser

    def extract_thread_urls(self, category_name: Text, category_url: Text, browser: uc.Chrome) -> Set[Text]:
        browser = self.open_an_url(category_url, browser)
        thread_urls = set()
        thread_cnt = 0
        page_cnt = 1
        with open(f"voz/URLs/{category_name}.txt", 'w') as out_f:
            while True:
                for thread in browser.find_elements(By.CSS_SELECTOR, 'div.structItem-title a:last-child'):
                    thread_url = thread.get_attribute('href')
                    thread_urls.add(thread_url)
                    out_f.write(thread_url + '\n')
                    thread_cnt += 1

                page = 'page-{}'
                next_page = browser.find_elements(By.CSS_SELECTOR, 'a.pageNav-jump--next')
                if page_cnt % 10 == 0 or not next_page:
                    print("Pass through %d pages" % page_cnt)
                    print("%d thread urls extracted!" % thread_cnt)
                    print("+++")
                    if not next_page:
                        break
                page_cnt += 1
                browser = self.open_an_url(category_url + page.format(page_cnt), browser)

        return thread_urls

    def extract_comments(self, url: Text, browser: uc.Chrome):
        browser = self.open_an_url(url, browser)
        title = browser.find_element(By.CSS_SELECTOR, 'h1.p-title-value').text
        data = []
        while True:
            for element in browser.find_elements(By.CSS_SELECTOR, 'div.message-userContent'):
                comment_id = element.get_attribute('data-lb-id').replace('post-', '')
                div_parse = BeautifulSoup(
                    element.find_element(By.CSS_SELECTOR, 'div.bbWrapper').get_attribute("innerHTML"))
                blockquote = div_parse.find('blockquote')
                prev_id = None
                if blockquote:
                    prev_id = blockquote.get('data-source').replace('post: ', '')
                    blockquote.decompose()
                content = div_parse.text.strip()
                data.append({'id': comment_id, 'content': content, 'parent_id': prev_id})

            next_page = browser.find_elements(By.CSS_SELECTOR, 'a.pageNav-jump--next')
            if next_page:
                browser.delete_all_cookies()
                next_page[0].click()
                time.sleep(self.DELAY_TIME)
            else:
                return data, title

    def get_all_category_urls(self, url: Text = None, browser: uc.Chrome = None) -> Dict[Text, Text]:
        if not browser: browser = self.init_browser()
        browser.get(url)
        categories = {}
        for category in browser.find_elements(By.CSS_SELECTOR, 'h3.node-title a'):
            category_name = category.text
            category_url = category.get_attribute('href')
            categories[category_name] = category_url
        return categories

    def get_all_thread_urls(self, categories: Dict[Text, Text], browser: uc.Chrome = None) -> Dict[Text, Set[Text]]:
        if not browser: browser = self.init_browser()
        urls_by_category = {}
        for category_name, category_url in categories.items():
            print(f'==={category_name}===')
            category_name = re.sub(r'\W+', '', category_name)
            if category_name in urls_by_category:
                continue
            urls = self.extract_thread_urls(category_name, category_url, browser)
            urls_by_category[category_name] = urls
        return urls_by_category

    def get_all_content(self, urls_by_category: Dict[Text, Set[Text]], browser: uc.Chrome = None) -> None:
        for category_name, thread_urls in urls_by_category.items():
            print(f'==={category_name}===')
            with open(f"voz/Threads/{category_name}.json", 'w') as out_f:
                cnt = 0
                for thread_url in thread_urls:
                    content_data, title = self.extract_comments(thread_url, browser)
                    json.dump({'url': thread_url, 'title': title.strip(), 'content': content_data},
                              out_f,
                              ensure_ascii=False)
                    out_f.write('\n')
                    cnt += 1
                    if cnt % int(0.1 * len(thread_urls)) == 0:
                        print('Extracted %d threads' % cnt)
