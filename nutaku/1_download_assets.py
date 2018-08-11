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
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(
    filename='1_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

codes = dict(nutaku={}, dmm={})
codes['nutaku']['kamihime'] = dict(
    intro=['94/76/', '76/89/'], scene=['de/59/'], get='76/89/')
codes['nutaku']['eidolon'] = dict(
    intro=['9f/51/'], scene=['d7/ad/'], get='9f/51/')
codes['nutaku']['soul'] = dict(
    intro=['67/01/', '3b/26/'], scene=['ec/4d/'], get='3b/26/')
codes['nutaku']['story'] = dict(intro=['44/89/', '4d/fd/', '3d/12/', '81/19/', 'ee/10/',
                                       '19/b4/'], scene=['92/ec/', '28/8f/', '91/1b/', '01/8d/', 'cc/d4/', '96/15/'])

base_url = dict(nutaku={}, dmm={})

base_url['nutaku']['fgimage'] = 'https://cf.static.r.kamihimeproject.dmmgames.com/scenarios/fgimage/'
base_url['nutaku']['bgm'] = 'https://cf.static.r.kamihimeproject.dmmgames.com/scenarios/bgm/'
base_url['nutaku']['bg'] = 'https://cf.static.r.kamihimeproject.dmmgames.com/scenarios/bgimage/'
base_url['nutaku']['scenarios'] = 'https://cf.static.r.kamihimeproject.dmmgames.com/scenarios/'

links = {'': []}

data_directory = 'raw_scenario'
asset_folder = 'assets'
character_types = os.listdir(data_directory)

for character_type in character_types:
    lst = os.listdir(os.path.join(data_directory, character_type))
    for character in lst:
        scenarios = os.listdir(os.path.join(data_directory, character_type, character))
        for filename in scenarios:
            print character, filename
            with open(os.path.join(data_directory, character_type, character, filename)) as file:
                data = json.load(file)

            type = character_type.split('_')[0]

            if data.has_key('scenario'):
                resource_directory = data['resource_directory']

                if not links.has_key(resource_directory):
                    links[resource_directory] = []

                data = data['scenario'].split('\n')
                for entry in data:
                    if entry.startswith('*') or entry.startswith('#') or entry.startswith('Tap to continue'):
                        continue
                    if entry.startswith('['):
                        entry = entry.replace('[', '').replace(
                            ']', '').replace('"', '').split()
                        if len(entry) < 2:
                            continue
                        # print entry
                        line = dict(cmd=entry[0])
                        for record in entry[1:]:
                            cmd = record.split('=')
                            if len(cmd) == 2:
                                line[cmd[0]] = cmd[1]
                        # print line

                        link = ''
                        if line['cmd'].startswith('chara_new') or line['cmd'].startswith('chara_face'):
                            link = base_url['nutaku']['fgimage'] + line['storage']
                            links[''].append((line['storage'], [link]))
                        elif line['cmd'].startswith('playbgm'):
                            link = base_url['nutaku']['bgm'] + line['storage']
                            links[''].append((line['storage'], [link]))
                        elif line['cmd'].startswith('bg'):
                            hd_link = re.sub(
                                r"(.*)(-.*)", r"\1_pc_h\2", line['storage'])
                            link = base_url['nutaku']['bg'] + hd_link
                            links[''].append((line['storage'], [link]))

                        # print type
                        link = []
                        if line['cmd'].startswith('playse'):
                            # print line['storage']
                            if line['storage'].startswith('h_intro') or line['storage'].startswith('h_get') or line['storage'].startswith('h_main') or line['storage'].startswith('se'):
                                for code in codes['nutaku'][type]['intro']:
                                    sub_link = base_url['nutaku']['scenarios']
                                    sub_link += code
                                    sub_link += resource_directory + \
                                        '/sound/' + line['storage']
                                    link.append(sub_link)

                            if len(link):
                                links[resource_directory].append(
                                    (line['storage'], link))

            elif data.has_key('scene_data'):
                resource_directory = data['resource_directory']
                if not links.has_key(resource_directory):
                    links[resource_directory] = []

                # print type
                # # sys.exit()
                for entry in data['scene_data']:
                    if entry.has_key('bgm'):
                        link = []
                        for code in codes['nutaku'][type]['scene']:
                            sub_link = base_url['nutaku']['scenarios']
                            sub_link += code + resource_directory + \
                                '/' + entry['bgm']
                            link.append(sub_link)
                        links[resource_directory].append((entry['bgm'], link))

                    if entry.has_key('film'):
                        link = []
                        for code in codes['nutaku'][type]['scene']:
                            sub_link = base_url['nutaku']['scenarios']
                            sub_link += code + resource_directory + \
                                '/' + entry['film']
                            link.append(sub_link)
                        links[resource_directory].append((entry['film'], link))

                    for line in entry['talk']:
                        if line.has_key('voice'):
                            link = []
                            for code in codes['nutaku'][type]['scene']:
                                sub_link = base_url['nutaku']['scenarios']
                                sub_link += code + resource_directory + \
                                    '/' + line['voice']
                                link.append(sub_link)
                            links[resource_directory].append((line['voice'], link))

headers = {}
headers['user-agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
s = requests.Session()
for resource_directory in links:
    for link in links[resource_directory]:
        folder = os.path.join(asset_folder, resource_directory)
        dst = os.path.join(folder, link[0])

        if not os.path.exists(folder):
            os.mkdir(folder)

        if not os.path.exists(dst):

            print "Saving", link
            if "black.jpg" in link:
                shutil.copyfile("black.jpg", dst)
            else:
                success = False
                for url in link[1]:
                    r = s.get(url, headers=headers, verify=False)
                    if r.status_code == 200 and not r.text.startswith('<html>'):
                        success = True
                        break
                if success:
                    with open(dst, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                else:
                    print "Error"
                    logging.error(link[1])
        else:
            print dst, 'already exists'
