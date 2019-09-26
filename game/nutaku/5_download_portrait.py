import requests
import re
import os
import io
import ConfigParser
import logging
from bs4 import BeautifulSoup
logging.basicConfig(
    filename='5_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

# img_folder = 'nutaku/portrait'
# config_file = 'nutaku/config.ini'
img_folder = 'portrait'
config_file = 'config.ini'

if not os.path.exists(img_folder):
    os.mkdir(img_folder)

s = requests.Session()

dom_kamihime = BeautifulSoup(s.get('http://kamihime-project.wikia.com/wiki/Kamihime').text, 'html.parser')
dom_eidolon = BeautifulSoup(s.get('http://kamihime-project.wikia.com/wiki/Eidolons').text, 'html.parser')
dom_soul = BeautifulSoup(s.get('http://kamihime-project.wikia.com/wiki/Souls').text, 'html.parser')

config = ConfigParser.RawConfigParser()
config.read(config_file)

for section in config.sections():
    if section.startswith('story'):
        continue

    char_name = config.get(section, 'name')

    if os.path.exists(os.path.join(img_folder, '%s.png' % char_name)):
        print '%s.png already exists' % char_name
        continue

    char_np = char_name.replace('\'', '&#039;')\
        .replace('Masamune', 'Masamune(Soul)')

    try:
        url = (dom_kamihime.find('img', {'alt': '%s Portrait' % char_np, 'width': '75'}) or
               dom_eidolon.find('img', {'alt': '%s Portrait' % char_np, 'width': '75'}) or
               dom_soul.find('img', {'alt': '%s Portrait' % char_np, 'width': '75'}))['data-src']
    except:
        print 'Can not find character %s' % char_np
        logging.error('Can not find character %s' % char_np)
        continue

    url = re.sub(r'(.*png).*', '\\1', url)
    print 'Downloading', char_name
    print 'url:', url
    r = s.get(url)

    if r.status_code <> requests.codes.ok:
        print 'Error downloading image: %d' % r.status_code
        logging.error('Error download img (%d): %s' % (url, r.status_code))

    with open(os.path.join(img_folder, '%s.png' % char_name), 'wb') as f:
        for chunk in r:
            f.write(chunk)
