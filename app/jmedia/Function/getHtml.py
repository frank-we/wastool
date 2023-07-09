import requests
import os
import cloudscraper
from config import Config


# ========================================================================获取config
def get_config():
    timeout = 10000
    retry_count = 5
    return timeout, retry_count


# ========================================================================获取proxies
def get_proxies():
    return Config().get_proxies()


# ========================================================================网页请求
# 破解cf5秒盾
def get_html_javdb(url):
    scraper = cloudscraper.create_scraper()
    # 发送请求，获得响应
    response = scraper.get(url)
    # 获得网页源代码
    html = response.text
    return html


def get_html(url, cookies=None):
    proxy_type = ''
    retry_count = 0
    proxy = ''
    timeout = 0
    try:
        timeout, retry_count = get_config()
    except Exception as error_info:
        print('Error in get_html :' + str(error_info))
        print('[-]Proxy config error! Please check the config.')
    proxies = get_proxies()
    i = 0
    while i < retry_count:
        try:
            headers = {
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/60.0.3100.0 Safari/537.36'
            }
            getweb = requests.get(str(url),
                                  headers=headers,
                                  timeout=timeout,
                                  proxies=proxies,
                                  cookies=cookies)
            getweb.encoding = 'utf-8'
            return getweb.text
        except Exception as error_info:
            i += 1
            print('Error in get_html :' + str(error_info))
            print('[-]Connect retry ' + str(i) + '/' + str(retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    return 'ProxyError'


def post_html(url: str, query: dict):
    proxy_type = ''
    retry_count = 0
    proxy = ''
    timeout = 0
    try:
        proxy_type, proxy, timeout, retry_count = get_config()
    except Exception as error_info:
        print('Error in post_html :' + str(error_info))
        print('[-]Proxy config error! Please check the config.')
    proxies = get_proxies(proxy_type, proxy)
    for i in range(retry_count):
        try:
            result = requests.post(url,
                                   data=query,
                                   proxies=proxies,
                                   timeout=timeout)
            result.encoding = 'utf-8'
            result = result.text
            return result
        except Exception as error_info:
            print('Error in post_html :' + str(error_info))
            print("[-]Connect retry {}/{}".format(i + 1, retry_count))
    print("[-]Connect Failed! Please check your Proxy or Network!")
    return 'ProxyError'
