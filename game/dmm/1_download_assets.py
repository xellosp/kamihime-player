import requests
import json
import os
import sys
import codecs
import subprocess
import shutil
import re
import urllib3
import logging
import ConfigParser
import posixpath
import threading
import concurrent.futures as cf
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(
    filename='1_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

# Number of threads to donwload assets
config = ConfigParser.RawConfigParser()
config.read('setting.ini')
thread_num = config.getint('script', 'threads')

# Set request timeout (seconds)
req_timeout = 120

ignore_links = []
retry_links = []
retry_num = 3

ignore_file = 'ignore.txt'

base_url = dict()

base_url['fgimage'] = 'https://static-r.kamihimeproject.net/scenarios/fgimage/'
base_url['bgm'] = 'https://static-r.kamihimeproject.net/scenarios/bgm/'
base_url['bg'] = 'https://static-r.kamihimeproject.net/scenarios/bgimage/'
base_url['scenarios'] = 'https://static-r.kamihimeproject.net/scenarios/'

if os.path.exists(ignore_file):
    with open(ignore_file, 'r') as f:
        ignore_links = f.read().splitlines()
    ignore_links_len = len(ignore_links)
else:
    ignore_links_len = 0

links = []

data_directory = 'raw_scenario'
asset_folder = 'assets'

if not os.path.exists(asset_folder):
    os.mkdir(asset_folder)

headers = {}
headers['user-agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
s = requests.Session()
        
############################################################################
# SYNCHRONIZED PRINT FUNCTION
############################################################################
def synchronized(func):
    func.__lock__ = threading.Lock()
		
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


@synchronized
def print_console(text):
    try:
        print text
    except:
        pass


############################################################################
# MAIN FUNCTIONS
############################################################################
def download_script(script_path, url):
    r = s.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        try:
            with open(script_path, 'w') as f:
                if script_path.endswith('json'):
                    content = re.sub('(\\],(?=\\s*\\}))', ']',
                                     re.sub('(\\},(?=\\s*\\]))', '}', r.text))
                    content = re.sub('(?!\\}),(?=\\s*\\})', '', content)
                    content = re.sub('\\];', ']', content)
                else:
                    content = r.text
                f.write(content.encode('utf-8'))
                f.flush()
        except:
            os.remove(script_path)
        return True
    else:
        return False


def download_asset(link, resource_directory):
    link = link.replace(' ', '')
    folder = os.path.join(asset_folder, resource_directory)
    dst = os.path.join(folder, link[link.rfind('/')+1:]).replace('_pc_h', '')

    if not os.path.exists(folder):
        os.mkdir(folder)

    if os.path.exists(dst):
        print_console('%s already exists' % dst)
    else:
        if link in ignore_links:
            print_console('Ignore %s' % link)
            return

        try:
            r = s.get(link, headers=headers, verify=False, timeout=req_timeout)
            if r.status_code == 200 and not r.text.startswith('<html>'):
                print_console("Saved %s" % link)
                with open(dst, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            else:
                print_console("Error: %s" % link)
                logging.error("%s (%s)" % (link, r.status_code))

                if r.status_code == 404:
                    ignore_links.append(link)
        except requests.exceptions.RequestException as e:
            retry_links.append(link, resource_directory)
            logging.error("%s: %s" % (link, e))


def download_assets(links, resource_directory=''):
    with cf.ThreadPoolExecutor(max_workers=thread_num) as executor:
        futures = [executor.submit(download_asset, link, resource_directory) for link in links]

        for _ in cf.as_completed(futures):
            pass


def download_scenario_assets(character, type, filename, data):
    script_file = '%s_script.ks' % filename.replace('.json', '').replace('.ks', '')
    script_path = os.path.join(data_directory, type, character, script_file)

    # Download script file if not exists
    if not os.path.exists(script_path):
        print "Downloading script file..."
        if not download_script(script_path, base_url['scenarios'] + data['scenario_path']):
            print "Failed to download script for %s" % filename
            logging.error('Failed to download script for %s' % filename)
            return

    with open(script_path) as file:
        script = file.read().decode("utf-8")

    links = []
    for match in re.finditer(r'\[chara_face.*storage="(.*)"', script):
        links.append(base_url['fgimage'] + match.group(1))

    for match in re.finditer(r'\[playbgm.*storage="(.*)"', script):
        links.append(base_url['bgm'] + match.group(1))

    for match in re.finditer(r'\[bg.*storage="(.*)"', script):
        links.append(base_url['bg'] + re.sub(r"(.*)(-.*)",
                                             r"\1_pc_h\2", match.group(1)))

    download_assets(links)

    links = []
    for match in re.finditer(r'\[playse.*storage="(.*)"', script):
        links.append(base_url['scenarios'] + '/'.join(
            data['scenario_path'].split('/')[:3]) + '/sound/' + match.group(1))

    download_assets(links, data['resource_directory'])


def download_hscene_assets(character, type, filename, data):
    script_file = '%s_script.json' % filename.replace('.json', '').replace('.ks', '')
    script_path = os.path.join(data_directory, type, character, script_file)

    # Download script file if not exists
    if not os.path.exists(script_path):
        print "Downloading script file..."
        if not download_script(script_path, base_url['scenarios'] + data['scenario_path']):
            print "Failed to download script for %s" % filename
            logging.error('Failed to download script for %s' % filename)
            return

    with open(script_path) as file:
        script = json.load(file)

    links = []
    resource_path = data['scenario_path'][:data['scenario_path'].rfind('/')]
    for section in script:
        if section.has_key('bgm'):
            download_assets([base_url['scenarios'] + resource_path + "/" + section['bgm']])
        if section.has_key('film'):
            links.append(base_url['scenarios'] + resource_path + "/" + section['film'])
        if section.has_key('talk'):
            for part in section['talk']:
                if part.has_key('voice'):
                    links.append(base_url['scenarios'] + resource_path + "/" + part['voice'])

    download_assets(links, data['resource_directory'])


# ---------------------------------------Start-------------------------------------------
if not os.path.exists(asset_folder):
    os.mkdir(asset_folder)

for type in os.listdir(data_directory):
    for character in os.listdir(os.path.join(data_directory, type).decode('utf8')):
        scenarios = os.listdir(os.path.join(data_directory, type, character))
        for filename in scenarios:
            if '_script' in filename:
                continue

            print_console(character + " " + filename)

            with open(os.path.join(data_directory, type, character, filename)) as file:
                data = json.load(file)

            if data['scenario_path'].endswith('.ks'):
                download_scenario_assets(character, type, filename, data)
            else:
                download_hscene_assets(character, type, filename, data)


for resource_directory in links:
    with cf.ThreadPoolExecutor(max_workers=thread_num) as executor:
        futures = [executor.submit(lambda p: download_asset(*p), (link, resource_directory)) for link in links[resource_directory]]

        for _ in cf.as_completed(futures):
            pass

# Retry error links
while retry_num > 0 and retry_links:
    print_console('Retrying error links...')
    tmp_links = retry_links
    retry_links = []

    with cf.ThreadPoolExecutor(max_workers=thread_num) as executor:
        futures = [executor.submit(lambda p: download_asset(*p), (retry_link[0], retry_link[1])) for retry_link in tmp_links]

        for _ in cf.as_completed(futures):
            pass

    retry_num = retry_num - 1

if len(ignore_links) != ignore_links_len:
    # Write new ignore links to file
    with open(ignore_file, 'a') as f:
        for link in ignore_links[ignore_links_len:]:
            f.write(link + '\n')