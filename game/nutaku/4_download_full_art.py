# -*- coding: utf-8 -*-
import requests
import re
import os
import io
import ConfigParser
import numpy as np
import logging
from PIL import Image
logging.basicConfig(
    filename='4_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

base_url = 'http://kamihime-project.wikia.com'
data_folder = 'raw_scenario'
img_folder = 'portrait_full'
config_file = 'config.ini'
info = {}

if not os.path.exists(img_folder):
    os.mkdir(img_folder)
s = requests.Session()
config = ConfigParser.RawConfigParser()
config.read(config_file)

for section in config.sections():
    if section.startswith('story'):
        continue

    char_name = config.get(section, 'name')

    if os.path.exists(os.path.join(img_folder, '%s.png' % char_name)):
        print '%s.png already exists' % char_name
        continue

    print 'Downloading', char_name
    url = base_url + '/wiki/' + char_name
    r = s.get(url)
    m = re.search('<a class="image lightbox" href="(.*?)"', r.text)
    if not m:
        print 'Error getting image url:', char_name
        logging.error('Error getting image url: %s' % char_name)
        continue

    url = base_url + m.group(1)
    r = s.get(url)
    m = re.search('meta property="og:image" content="(.*?)"', r.text)
    if not m:
        print 'Error getting image url:', char_name
        logging.error('Error getting image url: %s' % char_name)
        continue

    img_url = m.group(1)

    print 'url:', img_url
    r = s.get(img_url)

    if r.status_code <> requests.codes.ok:
        print 'Error downloading image: %d' % r.status_code
        logging.error('Error download img (%d): %s' % (img_url, r.status_code))

    im = Image.open(io.BytesIO(r.content))
    im = im.convert('RGBA')
    data = np.array(im)
    r, g, b, a = data.T
    a[a == a[0][0]] = 0
    img = Image.fromarray(data)
    img.save(os.path.join(img_folder, '%s.png' % char_name))
