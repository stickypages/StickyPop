from StickyBrowser import StickyBrowser


params = {
    'use_proxy': True,
    'proxy': {
        'http': 'http://ijpzpyhy-rotate:k9jutry0lqcc@p.webshare.io:80',
        'https': 'http://ijpzpyhy-rotate:k9jutry0lqcc@p.webshare.io:80'
    },
}
url = 'https://www.castanet.net/edition/news-story--11-.htm'

for x in range(5000):
    print(f'Voting {x} of 5000')
    browser = StickyBrowser(True, params)
    page = browser.get(url)
    page.find("input[type='radio'][value='2']").click()
    page.find("input[type='button'][value='Vote']").click()
    page.wait(1.75)
    browser.quit()


print('Done')
