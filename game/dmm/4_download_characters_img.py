# -*- coding: utf-8 -*-
import requests
import re
import os
import io
import urllib
import traceback
import ConfigParser
import numpy as np
import logging
from PIL import Image
from parsel import Selector
logging.basicConfig(
    filename='4_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

base_url = 'http://xn--hckqz0e9cygq471ahu9b.xn--wiki-4i9hs14f.com/index.php?'

data_folder = 'raw_scenario'
img_folder = 'portrait_full'
config_file = 'config.ini'
# data_folder = 'dmm/raw_scenario'
# img_folder = 'dmm/portrait_full'
# config_file = 'dmm/config.ini'

if not os.path.exists(img_folder):
    os.mkdir(img_folder)

s = requests.Session()
config = ConfigParser.RawConfigParser()


def log_console(text):
    try:
        print text
    except:
        None


config.read(config_file)
for section in config.sections():
    if section.startswith('story'):
        continue
        
    char_name = config.get(section, 'name').decode('utf-8')
    if os.path.exists(os.path.join(img_folder, '%s.png' % char_name)):
        log_console('%s.png already exists' % char_name)
        continue

    url = base_url + char_name.replace(u'(', u'［').replace(u')', u'］').replace(u'［神化覚醒］', '').replace(u'黄龍', u'黄竜').encode('utf-8')
    log_console('Downloading %s (%s)' % (char_name, url.decode('utf-8')))
    r = s.get(url)
    selector = Selector(r.text)
    portrait_text = u"全体絵  ".encode('utf-8')

    if char_name.endswith(u'(神化覚醒)'):
        img_url = selector.xpath(
            '//h3[contains(text(), portrait_text)]/following-sibling::table[1]/tr[1]/td[last()]/p[1]//img[3]/@src').extract_first()
        if img_url == None:
            img_url = selector.xpath(
                '//h3[contains(text(), portrait_text)]/following-sibling::table[1]/tr[1]/td[last()]/p[1]//img[2]/@src').extract_first()
    else:
        img_url = selector.xpath(
            '//h3[contains(text(), portrait_text)]/following-sibling::table[1]/tr[1]/td[last()]/p[1]//img[1]/@src').extract_first()

    try:
        log_console('url: %s' % img_url)
        r = s.get(img_url)

        if r.status_code <> requests.codes.ok:
            log_console('Error downloading image: %d' % r.status_code)
            logging.error('Error downloading image: %d' % r.status_code)

        im = Image.open(io.BytesIO(r.content))
        im = im.convert('RGBA')
        data = np.array(im)
        r, g, b, a = data.T
        a[a == a[0][0]] = 0
        img = Image.fromarray(data)
        img.save(os.path.join(img_folder, '%s.png' % char_name))
    except:
        log_console('Error downloading image')
        logging.error('Downloading %s: (%s)' % (char_name, img_url))
        logging.error(traceback.format_exc())
