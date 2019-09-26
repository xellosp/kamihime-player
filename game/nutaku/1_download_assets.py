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
import threading
import pickle
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

if os.path.exists(ignore_file):
    with open(ignore_file, 'r') as f:
        ignore_links = f.read().splitlines()
    ignore_links_len = len(ignore_links)
else:
    ignore_links_len = 0

base_url = dict(nutaku={}, dmm={})

base_url['fgimage'] = 'https://cf.static.r.kamihimeproject.dmmgames.com/scenarios/fgimage/'
base_url['bgm'] = 'https://cf.static.r.kamihimeproject.dmmgames.com/scenarios/bgm/'
base_url['bg'] = 'https://cf.static.r.kamihimeproject.dmmgames.com/scenarios/bgimage/'
base_url['scenarios'] = 'https://cf.static.r.kamihimeproject.dmmgames.com/scenarios/'

links = {'': []}

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
def download_script(file_path, url):
    r = s.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.text
    else:
        print 'Failed to download script for "%s"' % file_path
        sys.exit()


def write_to_file(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f)
    except:
        print 'Failed to convert file "%s"' % file_path
        sys.exit()


def download_scenario_script(file_path, data):
    url = base_url['scenarios'] + data['scenario_path']
    script = download_script(file_path, url)
    data.update({'scenario': '%s' % script})
    write_to_file(file_path, data)
    return data


def download_hscene_script(file_path, data):
    url = base_url['scenarios'] + data['scenario_path']
    script = download_script(file_path, url)
    script = re.sub('(\\],(?=\\s*\\}))', ']', re.sub('(\\},(?=\\s*\\]))', '}', script))
    script = re.sub('(?!\\}),(?=\\s*\\})', '', script)
    script = re.sub('\\];', ']', script)
    script = json.loads(script)
    data.update({'scene_data': script})
    write_to_file(file_path, data)
    return data


def download_asset(link, resource_directory):
    link = link.replace(' ', '')
    folder = os.path.join(asset_folder, resource_directory)
    dst = os.path.join(folder, link[link.rfind('/')+1:]).replace('_pc_h', '')

    if not os.path.exists(folder):
        os.mkdir(folder)

    if not os.path.exists(dst):
        if "black.jpg" in link:
            shutil.copyfile("black.jpg", dst)
        else:
            if link in ignore_links:
                print_console('Ignore %s' % link)
                return

            try:
                r = s.get(link, headers=headers, verify=False, timeout=req_timeout)
                if r.status_code == 200 and not r.text.startswith('<html>'):
                    print_console('Saved %s' % link)
                    with open(dst, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                else:
                    print_console('Error: %s' % link)
                    logging.error("%s (%s)" % (link, r.status_code))

                    if r.status_code == 404:
                        ignore_links.append(link)
            except requests.exceptions.RequestException as e:
                retry_links.append(link, resource_directory)
                logging.error("%s: %s" % (link, e))
    else:
        print_console('%s already exists' % dst)


character_types = os.listdir(data_directory)
for character_type in character_types:
    lst = os.listdir(os.path.join(data_directory, character_type).decode('utf8'))
    for character in lst:
        scenarios = os.listdir(os.path.join(data_directory, character_type, character))
        for filename in scenarios:
            print_console(character + " " + filename)
            file_path = os.path.join(data_directory, character_type, character, filename)
            with open(file_path) as file:
                data = json.load(file)

            type = character_type.split('_')[0]

            if data['scenario_path'].endswith('.ks'):
                if not data.has_key('scenario'):
                    print 'Convert script file...'
                    data = download_scenario_script(file_path, data)

                resource_directory = data['resource_directory']

                if not links.has_key(resource_directory):
                    links[resource_directory] = []

                resource_code = '/'.join(data['scenario_path'].split('/')[:2]) + '/'
                data = data['scenario'].replace('\r', '').split('\n')

                for entry in data:
                    if entry.startswith('*') or entry.startswith('#') or entry.startswith('Tap to continue'):
                        continue
                    if entry.startswith('['):
                        entry = entry.replace('[', '').replace(']', '').replace('"', '').split()

                        if len(entry) < 2:
                            continue

                        line = dict(cmd=entry[0])
                        for record in entry[1:]:
                            cmd = record.split('=')
                            if len(cmd) == 2:
                                line[cmd[0]] = cmd[1]

                        link = ''
                        if line['cmd'].startswith('chara_new') or line['cmd'].startswith('chara_face'):
                            link = base_url['fgimage'] + line['storage']
                            links[''].append(link)
                        elif line['cmd'].startswith('playbgm'):
                            link = base_url['bgm'] + line['storage']
                            links[''].append(link)
                        elif line['cmd'].startswith('bg'):
                            hd_link = re.sub(r"(.*)(-.*)", r"\1_pc_h\2", line['storage'])
                            link = base_url['bg'] + hd_link
                            links[''].append(link)

                        # print type
                        if line['cmd'].startswith('playse'):
                            # print line['storage']
                            if line['storage'].startswith('h_intro') or line['storage'].startswith('h_get') or line['storage'].startswith('h_main') or line['storage'].startswith('se'):
                                link = base_url['scenarios'] + resource_code + resource_directory + '/sound/' + line['storage']
                                links[resource_directory].append(link)

            else:
                if not data.has_key('scene_data'):
                    print 'Convert script file...'
                    data = download_hscene_script(file_path, data)

                resource_directory = data['resource_directory']
                if not links.has_key(resource_directory):
                    links[resource_directory] = []

                resource_code = '/'.join(data['scenario_path'].split('/')[:2]) + '/'
                
                for entry in data['scene_data']:
                    if entry.has_key('bgm'):
                        link = base_url['scenarios'] + resource_code + resource_directory + '/' + entry['bgm']
                        links[resource_directory].append(link)

                    if entry.has_key('film'):
                        link = base_url['scenarios'] + resource_code + resource_directory + '/' + entry['film']
                        links[resource_directory].append(link)

                    for line in entry['talk']:
                        if line.has_key('voice'):
                            link = base_url['scenarios'] + resource_code + resource_directory + '/' + line['voice']
                            links[resource_directory].append(link)


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