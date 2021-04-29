import random
import time
import json
from seleniumwire import webdriver
#from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.expected_conditions import presence_of_element_located


class StickyBrowser(object):
    def __init__(self, headless=True, additional_params={}, window_size='1920,1080'):
        self.AGENTS = []
        self.PROXIES = []
        self.URL = ''
        self.SOURCE = ''
        self.driver_location = '' #Does nothing atm

        self.PARAMS = {
            'use_proxy': False,
            'proxy': {},
            'rotate_proxy': False,
            'proxy_file': False,
            'user_agents': []
        }
        if additional_params:
            self.PARAMS = self.merge(self.PARAMS, additional_params)

        self.OPTIONS = webdriver.ChromeOptions()
        self.OPTIONS.add_argument('--no-sandbox')
        self.OPTIONS.add_argument('--disable-dev-shm-usage')
        self.OPTIONS.add_argument('--disable-gpu')
        self.OPTIONS.add_argument('--disable-features=NetworkService')
        self.OPTIONS.add_argument('--disable-features=VizDisplayCompositor')

        if window_size:
            self.OPTIONS.add_argument(f'window-size={window_size}')

        if headless:
            self.OPTIONS.add_argument('--headless')

        self.__user_agents()

        # RUN DRIVER
        self.DRIVER = webdriver.Chrome(ChromeDriverManager().install(),
                                       options=self.OPTIONS,
                                       seleniumwire_options=self.selenium_options())

    def __user_agents(self):
        self.AGENTS = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]
        if self.PARAMS['user_agents']:
            self.AGENTS = self.merge(self.AGENTS, self.PARAMS['user_agents'])

    def __proxies(self):
        if self.PARAMS['rotate_proxy']:
            if len(self.PROXIES) == 0:
                print('Load Proxies')
                with open(self.PARAMS['proxy_file']) as j:
                    proxy = json.load(j)
                    for p in proxy['data']:
                        self.PROXIES.append(p['ip'] + ':' + p['port'])
            else:
                print('Use Current Proxies')
                print(self.PROXIES)

            print(f'{len(self.PROXIES)} Proxies Loaded')

    def selenium_options(self):
        opt = {}
        if self.PARAMS['use_proxy']:
            opt = {
                'proxy': {
                    'http': 'http://stickypages:872283@ca-hl2-smart.serverlocation.co:3128',
                    'https': 'http://stickypages:872283@ca-hl2-smart.serverlocation.co:3128',
                    # 'http': 'http://ijpzpyhy-rotate:k9jutry0lqcc@p.webshare.io:80',
                    # 'https': 'http://ijpzpyhy-rotate:k9jutry0lqcc@p.webshare.io:80'
                }
            }
            if self.PARAMS['proxy']:
                opt = self.PARAMS['proxy']

        if self.PARAMS['rotate_proxy']:
            choice = random.choice(self.PROXIES)
            opt['proxy']['http'] = 'http://' + choice
            opt['proxy']['https'] = 'http://' + choice

        print(f'Selenium Options: {opt}')
        return opt

    def request_interceptor(self, request):
        del request.headers['User-Agent']
        request.headers['User-Agent'] = random.choice(self.AGENTS)

        del request.headers['Accept']
        request.headers[
            'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'

        del request.headers['Accept-Encoding']
        request.headers['Accept-Encoding'] = 'gzip, deflate'

        del request.headers['Accept-Language']
        request.headers['Accept-Language'] = 'en-CA,en-US;q=0.9,en;q=0.8'

        del request.headers['Upgrade-Insecure-Requests']
        request.headers['Upgrade-Insecure-Requests'] = '1'

    def response_interceptor(self, request, response):
        # The body is in bytes so convert to a string
        if response.body:
            if 'ipify.org' in self.URL:
                body = response.body.decode('utf-8')
                data = json.loads(body)
                print(data['ip'])

    def quit(self):
        # QUIT Browser
        print('QUIT')
        self.DRIVER.quit()

    def get(self, url, wait_for_driver=2):
        self.URL = url

        self.DRIVER.request_interceptor = self.request_interceptor
        self.DRIVER.response_interceptor = self.response_interceptor

        WebDriverWait(self.DRIVER, wait_for_driver)

        try:
            self.DRIVER.get(self.URL)
            print(f'Get URL: {self.URL}')
        except WebDriverException as ex:
            print(ex)

        return self

    def find(self, selector):
        try:
            self.element = WebDriverWait(self.DRIVER, 5).until(lambda d: d.find_element_by_css_selector(selector))
            # self.element = self.DRIVER.find_element_by_css_selector(selector)
            print(f' Element found ({selector}).')
            return self
        except NoSuchElementException as ex:
            print(f'Element not found ({selector}). {ex}')

    def click(self):
        print(f' Element CLICKED.')
        self.element.click()

    def submit(self):
        print(f' Send Keys: RETURN/SUBMIT')
        self.element.send_keys(Keys.RETURN)

    def input(self, text):
        print(f' INPUT: {text}')
        self.element.send_keys(text)

    # outerHTML | innerHTML | text
    def source(self, attribute='innerHTML'):
        if attribute == 'body':
            return self.DRIVER.execute_script("return document.body.innerHTML;")
        else:
            return self.element.get_attribute(attribute)

    def attr(self, attr):
        return self.element.get_attribute(attr)

    def document_initialised(self):
        return self.DRIVER.execute_script("return initialised")

    @staticmethod
    def merge(dict1, dict2):
        return {**dict1, **dict2}

    @staticmethod
    def response(self, driver):
        for request in driver.requests:
            if request.status_code:
                print(request.status_code)
        return self

    @staticmethod
    def wait(seconds):
        print(f'Waiting {seconds} seconds')
        time.sleep(seconds)
