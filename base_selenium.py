from typing import Text, Dict, List, Any, Set
import undetected_chromedriver as uc


class BaseSeleniumCrawler:
    base_url: str
    DELAY_TIME: int = 1

    @staticmethod
    def init_browser():
        options = uc.ChromeOptions()
        options.add_argument("--enable-javascript")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        options.add_argument('--no-sandbox')
        options.add_argument(
            "user-agent={ Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, "
            "like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36 }")
        browser = uc.Chrome(options=options)
        return browser

    def open_an_url(self, url: Text, browser: uc.Chrome):
        raise NotImplementedError()

    def extract_thread_urls(self, category_name: Text, category_url: Text, browser: uc.Chrome) -> Set[Text]:
        raise NotImplementedError()

    def extract_comments(self, url: Text, browser: uc.Chrome):
        raise NotImplementedError()

    def get_all_category_urls(self, url: Text = None, browser: uc.Chrome = None) -> Dict[Text, Text]:
        raise NotImplementedError()

    def get_all_thread_urls(self, categories: Dict[Text, Text], browser: uc.Chrome = None) -> Dict[Text, Set[Text]]:
        raise NotImplementedError()

    def get_all_content(self, urls_by_category, browser=None):
        raise NotImplementedError()

    def crawl(self):
        categories = self.get_all_category_urls(self.base_url)
        urls_by_category = self.get_all_thread_urls(categories)
        self.get_all_content(urls_by_category)
        return True

