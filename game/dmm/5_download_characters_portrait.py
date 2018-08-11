# -*- coding: utf-8 -*-
import requests
import re
import os
import io
import ConfigParser
import logging
from bs4 import BeautifulSoup
from parsel import Selector
logging.basicConfig(
    filename='5_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

img_folder = 'portrait'
config_file = 'config.ini'
# img_folder = 'dmm/portrait'
# config_file = 'dmm/config.ini'

if not os.path.exists(img_folder):
    os.mkdir(img_folder)

s = requests.Session()


def get_img_urls(link, is_soul=False):
    r = s.get(link)
    selector = Selector(r.text)
    if is_soul:
        names = selector.xpath('//div[@id="body"]/div[contains(@class, \"ie5\")]/table/tbody/tr/td[1]/a/text()').extract()
    else:
        names = selector.xpath('//div[contains(@class, "ie5")]/table/tbody/tr/td[2]/a/text()').extract()
    img_links = selector.xpath('//div[@id="body"]/div[contains(@class, "ie5")]/table/tbody//img[not(contains(@title, "edit"))]/@src').extract()
    return dict(zip(names, img_links))


def log_console(text):
    try:
        print text
    except:
        None


log_console('Getting character info...')
img_links = dict(get_img_urls(u'http://xn--hckqz0e9cygq471ahu9b.xn--wiki-4i9hs14f.com/index.php?SSR神姫'))
img_links.update(get_img_urls(u'http://xn--hckqz0e9cygq471ahu9b.xn--wiki-4i9hs14f.com/index.php?SR神姫'))
img_links.update(get_img_urls(u'http://xn--hckqz0e9cygq471ahu9b.xn--wiki-4i9hs14f.com/index.php?R神姫'))
img_links.update(get_img_urls(u'http://xn--hckqz0e9cygq471ahu9b.xn--wiki-4i9hs14f.com/index.php?SSR幻獣'))
img_links.update(get_img_urls(u'http://xn--hckqz0e9cygq471ahu9b.xn--wiki-4i9hs14f.com/index.php?SR幻獣'))
img_links.update(get_img_urls(u'http://xn--hckqz0e9cygq471ahu9b.xn--wiki-4i9hs14f.com/index.php?英霊性能一覧', True))

config = ConfigParser.RawConfigParser()
config.read(config_file)

for section in config.sections():
    char_name = config.get(section, 'name').decode('utf-8')
    if os.path.exists(os.path.join(img_folder, '%s.png' % char_name)):
        log_console('%s.png already exists' % char_name)
        continue

    try:
        url = img_links[char_name.replace(u'(', u'［').replace(u')', u'］').replace(u'［神化覚醒］', '').replace(u'黄龍', u'黄竜')]
    except:
        log_console('Can not find character %s' % char_name)
        logging.error('Can not find character %s' % char_name)
        continue

    log_console('Downloading %s' % char_name)
    log_console('url: %s' % url)
    r = s.get(url)

    if r.status_code <> requests.codes.ok:
        log_console('Error downloading image: %d' % r.status_code)
        logging.error('Error downloading image: %d' % url)

    with open(os.path.join(img_folder, '%s.png' % char_name), 'wb') as f:
        for chunk in r:
            f.write(chunk)
