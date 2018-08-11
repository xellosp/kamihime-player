import requests
import json
import os
import sys
import urllib3
import logging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(
    filename='0_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

xsrf = raw_input('XSRF-TOKEN: ')
session = raw_input('session: ')

headers = {}
# headers['cookie'] = 'XSRF-TOKEN=eyJpdiI6IjhqYnQwUEFtbXIrRlo4SmhnSkIyeGc9PSIsInZhbHVlIjoiYjlpdktQTStKSDNUK0JQWHJLejl0dGZ3TkttbzQybWJldlowZjBabGQxb0UwSUxPZUxsYWpXWlwveXlJeVV3ZUJWNDl4TzNQYVJLSzNZQlwvWklaSlU2Zz09IiwibWFjIjoiZWFkODRkY2U4YjcwMjY3OGFkMzk4MWM3MDJmZWFjMWIzNGIzNjgyYzE4NzZhNTkzNmM3MDcwZjU1M2ZhZjIzMSJ9; session=eyJpdiI6IjlpMUZQT0NzRkl3NnJKQzVMWndIWGc9PSIsInZhbHVlIjoiVEJMN2VvK2pFZ0RENlZLSWZKdWlBeWdLUXdUSWJDZ0Fva3lDS1ZqUGFsTkRTZzNiNm5CaG9qMlJHUWs3YzNKa2pNRTJGdmhuclN2b1dtZG96a2FLRWc9PSIsIm1hYyI6IjQ2ZTExZDkyYjczY2MwNjQ1YzNlYTRhMTVmZDA3MjZlNmViZmFjMDY1OWQzMzE5MjRjNjhkNGEyOTAzNDQ3NDEifQ%3D%3D'
headers['cookie'] = 'XSRF-TOKEN=%s;session=%s' % (xsrf, session)
headers['user-agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

kh_info_folder = "info_kamihime"
eid_info_folder = "info_eidolon"

if not os.path.exists(kh_info_folder):
    os.mkdir(kh_info_folder)
if not os.path.exists(eid_info_folder):
    os.mkdir(eid_info_folder)

s = requests.Session()

def download_info(link, info_folder):
    r = s.get(url, headers=headers, verify=False)
    j = json.loads(r.text)
    if r.status_code == requests.codes.forbidden:
        print 'Forbidden'
    elif r.status_code == 440:
        print 'Token incorrect or has expired'
        logging.error('Token incorrect or has expired')
        sys.exit()
    elif j.has_key('errors'):
        print 'Error: %s' % j['errors']
        logging.error('Error: %s' % j['errors'])
        sys.exit()
    elif r.status_code == requests.codes.ok:
        print 'OK'
        with open(os.path.join(info_folder, "%s.json" % id), 'w') as outfile:
            outfile.write(json.dumps(j, indent=4, sort_keys=True))
    else:
        print r.status_code
        logging.error('Error: %s' % r.status_code) 


kh_list = set(os.listdir(kh_info_folder))
print 'Download kamihime info...'
for x in (0, 5, 6, 7):
    for y in xrange(99):
        id = str(x*1000 + y + 1)
        if (id + '.json') not in kh_list:
            url = 'https://r.kamihimeproject.net/v1/characters/%s' % id
            print url
            download_info(url, kh_info_folder)
        else:
            print '%s already exists' % (id + '.json')

eid_list = set(os.listdir(eid_info_folder))
print 'Download eidolon info...'
for x in (0, 1, 2, 5, 6, 9):
    range = 300 if x == 0 else 100
    for y in xrange(range):
        id = str(x*1000 + y + 1)
        if (id + '.json') not in eid_list:
            url = 'https://r.kamihimeproject.net/v1/a_library/summons/%s' % id
            print url
            download_info(url, eid_info_folder)
        else:
            print '%s already exists' % (id + '.json')
