import requests
import json
import os
import sys
import urllib
import urllib3
import logging
import ConfigParser
import threading
import concurrent.futures as cf
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(
    filename='0_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

# Number of threads to donwload assets
config = ConfigParser.RawConfigParser()
config.read('setting.ini')
thread_num = config.getint('script', 'threads')

xsrf = raw_input('XSRF-TOKEN: ').strip()
session = raw_input('session: ').strip()

base_url = dict(soul={}, kamihime={}, eidolon={})
base_url['kamihime']['info'] = 'https://cf.r.kamihimeproject.dmmgames.com/v1/characters/'
base_url['kamihime']['scenes'] = 'https://cf.r.kamihimeproject.dmmgames.com/v1/gacha/harem_episodes/characters/'
base_url['eidolon']['info'] = 'https://cf.r.kamihimeproject.dmmgames.com/v1/summons/'
base_url['eidolon']['scenes'] = 'https://cf.r.kamihimeproject.dmmgames.com/v1/gacha/harem_episodes/summons/'
base_url['episode'] = 'https://cf.r.kamihimeproject.dmmgames.com/v1/episodes/'
base_url['scene'] = 'https://cf.r.kamihimeproject.dmmgames.com/v1/scenarios/'

soul_info_folder = "info_soul"
kh_info_folder = "info_kamihime"
eid_info_folder = "info_eidolon"
data_directory = 'raw_scenario'
soul_scenario = os.path.join(data_directory, "soul")
eid_scenario = os.path.join(data_directory, "eidolon")
khr_scenario = os.path.join(data_directory, "kamihime_R")
khsr_scenario = os.path.join(data_directory, "kamihime_SR")
khssr_scenario = os.path.join(data_directory, "kamihime_SSR")

if not os.path.exists(soul_info_folder):
    os.mkdir(soul_info_folder)
if not os.path.exists(kh_info_folder):
    os.mkdir(kh_info_folder)
if not os.path.exists(eid_info_folder):
    os.mkdir(eid_info_folder)
if not os.path.exists(data_directory):
    os.mkdir(data_directory)
if not os.path.exists(soul_scenario):
    os.mkdir(soul_scenario)
if not os.path.exists(eid_scenario):
    os.mkdir(eid_scenario)
if not os.path.exists(khr_scenario):
    os.mkdir(khr_scenario)
if not os.path.exists(khsr_scenario):
    os.mkdir(khsr_scenario)
if not os.path.exists(khssr_scenario):
    os.mkdir(khssr_scenario)

episodes = dict()
souls = os.listdir(soul_scenario.decode('utf8'))
eidolons = os.listdir(eid_scenario.decode('utf8'))
kamihime_Rs = os.listdir(khr_scenario.decode('utf8'))
kamihime_SRs = os.listdir(khsr_scenario.decode('utf8'))
kamihime_SSRs = os.listdir(khssr_scenario.decode('utf8'))

for soul in souls:
    eps = [e.replace('.json', '') for e in os.listdir(os.path.join(data_directory, "soul", soul))]
    for episode in eps:
        episodes[episode] = soul

for eidolon in eidolons:
    eps = [e.replace('.json', '') for e in os.listdir(os.path.join(data_directory, "eidolon", eidolon))]
    for episode in eps:
        episodes[episode] = eidolon

for kamihime in kamihime_Rs:
    eps = [e.replace('.json', '') for e in os.listdir(os.path.join(data_directory, "kamihime_R", kamihime))]
    for episode in eps:
        episodes[episode] = kamihime

for kamihime in kamihime_SRs:
    eps = [e.replace('.json', '') for e in os.listdir(os.path.join(data_directory, "kamihime_SR", kamihime))]
    for episode in eps:
        episodes[episode] = kamihime

for kamihime in kamihime_SSRs:
    eps = [e.replace('.json', '') for e in os.listdir(os.path.join(data_directory, "kamihime_SSR", kamihime))]
    for episode in eps:
        episodes[episode] = kamihime

headers = {}
# headers['cookie'] = 'XSRF-TOKEN=eyJpdiI6ImlhbklwMEVYMm9raGMzUlZtWEJVY1E9PSIsInZhbHVlIjoicmliRG1SXC9sQTJ1RzRnT3F3VVNKKytXemx2TUhPRDgwWElNVUFvRVJWNTl0a3NOZEtkT0Y0RFVQZElXdWVyVTV5azlcL0xLYldwNU9lZHM0MGl5MHRndz09IiwibWFjIjoiMDNkNGMwMWU5N2ExNzFlOTZjNzNkY2NiODM4Y2NhMmUzZjg5YWZkZjE0MTkyOTgyY2FiNmE2YWEyMDMxNTM1OCJ9; session=eyJpdiI6Inh4QmVadVY4UTRKb1pvUndMSHJtcnc9PSIsInZhbHVlIjoiVVFrU2ExWkhPNE43VW1TY2ZoNUVsQUJ2VmlxUndoVlMwaXo5Y3Y0UGg2bnl4YnVQdjBtSFUyRWttWG9iWEhuU1o0Z3BDNHdjZVBaY1NvMlBocmRnaUE9PSIsIm1hYyI6ImIzNmVlYWIyYTc2ZGVhNDIwN2IxMGRjNTA1ZjBkYzJjNjIzZjU4MWFjMjE5Y2RhZjc4NzNhZDdiMTFiMTA3YzkifQ%3D%3D'
headers['cookie'] = 'XSRF-TOKEN=%s;session=%s' % (xsrf, session)
headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
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
# COMMON FUNCTIONS
############################################################################
def save_info(info_folder, file_name, data):
    file_path = os.path.join(info_folder, file_name)
    print_console("Saving %s" % file_path)
    with open(file_path, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4, sort_keys=True))


def save_script(_type, char_name, file_name, data):
    file_path = os.path.join(data_directory, _type, char_name, file_name)
    print_console("Saving %s" % file_path)
    with open(file_path, 'w') as outfile:
        outfile.write(json.dumps(data, indent=4, sort_keys=True))


def download_info(id, link, info_folder):
    r = s.get(link, headers=headers, verify=False)
    info = json.loads(r.text)
    if r.status_code == requests.codes.forbidden:
        print_console('Forbidden: %s' % link)
        return None
    elif r.status_code == 440:
        print_console('Token incorrect or has expired')
        logging.error('Token incorrect or has expired')
        sys.exit()
    elif info.has_key('errors'):
        print_console('Error: %s\n%s' % (info['errors'], link))
        logging.error('Error: %s\n%s' % (info['errors'], link))
        sys.exit()
    elif r.status_code == requests.codes.ok:
        print_console('OK: %s' % link)
        save_info(info_folder, "%s.json" % id, info)
        return info
    else:
        print_console(r.status_code)
        logging.error('Error (%s): %s' % (r.status_code, link)) 
        return None


def load_info(info_folder, id):
    with open(os.path.join(info_folder, id + '.json')) as file:
        return json.load(file)


############################################################################
# SOUL FUNCTIONS
############################################################################
def download_souls_info():
    ### Download info of all souls.###
    url = 'https://cf.r.kamihimeproject.dmmgames.com/v1/a_jobs'
    r = s.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return json.loads(r.text)['data']
    else:
        info=[]
        for acquire in (True, False):
            for rank in ("basic", "upper", "uppermost"):
                query = {"acquired": acquire, "rank": rank}
                params = "?json=%s" % urllib.quote(json.dumps(query))
                r = s.get(url + params, headers=headers, verify=False)
                info.extend(json.loads(r.text)['data'])
        return info


def download_soul_episodes_info(soul_info):
    ### Donwload and save sould scenes info into info_soul folder.###
    scenes = []
    job_id = soul_info['job_id']
    if (job_id <= 30):
        # Tier 3 and below souls
        url_ids = [job_id * 2 - 1, job_id * 2]
    else:
        # Tier 4 souls
        url_ids = [job_id * 100 + 1, job_id * 100 + 2]
    
    for url_id in url_ids:
        url = base_url['episode'] + str(url_id) + "_harem-job"
        
        r = s.get(url, headers=headers, verify=False)
        if r.status_code == 200:
            print_console('OK: %s' % url)
            data = json.loads(r.text)
            scenario = data['chapters'][0]['scenarios'][0]

            scenes.append({
                "id": scenario['scenario_id'],
                "resource_directory": scenario['resource_directory']
            })

            if data['chapters'][0].has_key('harem_scenes'):
                harem_scene = data['chapters'][0]['harem_scenes'][0]
                scenes.append({
                    "id": harem_scene['harem_scene_id'],
                    "resource_directory": harem_scene['resource_directory']
                })
        else:
            print_console('Unable to download: %s' % url)
            logging.error('Error: %s - url: %s' % (r.status_code, url))
        
    soul_info['episodes'] = scenes
    save_info(soul_info_folder, str(job_id) + '.json', soul_info)
    return soul_info


def download_soul_script(info):
    ### Download and save soul scene script into raw_scenario folder.###
    character_name = info['name']
    
    # Check available scenes
    scenes = info['episodes']
    ep_infos = dict()
    name = None

    for scene in scenes:
        file_name = scene['id']
        resource_directory = scene['resource_directory']

        if episodes.has_key(file_name):
            name = episodes[file_name]
        else:
            resource_code = '/'.join([resource_directory[-4:][i:i+2] for i in range(0, len(resource_directory[-4:]), 2)])
            scene_idx = scenes.index(scene)
            if scene_idx in [0, 1]:
                url = base_url['scene'] + file_name
                r = s.get(url, headers=headers, verify=False)
                if r.status_code == 200:
                    scene_info = json.loads(r.text)
                else:
                    scene_info = {
                        "scenario_path": "%s/%s/scenario/first.ks" % (resource_code, resource_directory),
                        "title": "No data",
                        "summary": "No data",
                        "resource_directory": resource_directory
                    }
            else:
                scene_info = {
                    "scenario_path": "%s/%s/scenario.json" % (resource_code, resource_directory),
                    "resource_directory": resource_directory
                }

            ep_infos[file_name] = scene_info

    if name == None:
        name = character_name
        path = os.path.join(data_directory, "soul", name)
        if not os.path.exists(path):
            os.mkdir(os.path.join(data_directory, "soul", name))

    # Write to folder
    for file_name in ep_infos:
        save_script("soul", name, file_name + '.json', ep_infos[file_name])


############################################################################
# KAMIHIME FUNCTIONS
############################################################################
def download_kamihime_episodes_info(info):
    ### Download and save kamihime info to info_kamihime folder.### 
    url = base_url['kamihime']['scenes'] + str(info['character_id'])
    r = s.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        info_ep_1 = json.loads(r.text)
        ep_1_id = int(info_ep_1['episode_id'].split('_')[0])
        eps = [ep_1_id - 1, ep_1_id]
        if info['rare'] == 'SR' or (info['rare'] == 'SSR' and 'Awakened' not in info['name']):
            eps.append(ep_1_id + 1)
        
        scenes = []
        for ep in eps:
            r = s.get(base_url['episode'] + str(ep) + "_harem-character", headers=headers, verify=False)
            if r.status_code == 200:
                data = json.loads(r.text)
                scenario = data['chapters'][0]['scenarios'][0]
                scenes.append({
                    "id": scenario['scenario_id'],
                    "resource_directory": scenario['resource_directory'],
                    "title": "No data" if eps.index(ep) <> 1 else info_ep_1['title'],
                    "description": "No data" if eps.index(ep) <> 1 else info_ep_1['description']
                })

                if data['chapters'][0].has_key('harem_scenes'):
                    harem_scene = data['chapters'][0]['harem_scenes'][0]
                    scenes.append({
                        "id": harem_scene['harem_scene_id'],
                        "resource_directory": harem_scene['resource_directory']
                    })
                elif eps.index(ep) == 1:
                    # Non-lewd character
                    if info['rare'] == 'R':
                        eps.append(ep_1_id + 1)
                    if len(scenes) <> 1:
                        for i in range(0, len(scenes) - 1):
                            scenes.pop(0)
            else:
                if info['rare'] == 'R':
                    eps.append(ep_1_id + 1)
                    
        info['episodes'] = scenes
        save_info(kh_info_folder, str(info['character_id']) + '.json', info)
    else:
        print_console('Unable to download: %s' % url)
        logging.error('Error: %s - url: %s' % (r.status_code, url))

    return info


def download_kamihime_script(info):
    character_name = info['name']
    rarity = info['rare']

    if not info.has_key('episodes'):
        info = download_kamihime_episodes_info(info)
    
    # Check available scenes
    scenes = info['episodes']
    ep_infos = dict()
    name = None

    for scene in scenes:
        file_name = scene['id']
        resource_directory = scene['resource_directory']

        if episodes.has_key(file_name):
            name = episodes[file_name]
        else:
            resource_code = '/'.join([resource_directory[-4:][i:i+2] for i in range(0, len(resource_directory[-4:]), 2)])
            scene_idx = scenes.index(scene)
            if scene_idx in [0, 1, 3]:
                url = base_url['scene'] + file_name
                r = s.get(url, headers=headers, verify=False)
                if r.status_code == 200:
                    scene_info = json.loads(r.text)
                else:
                    scene_info = {
                        "scenario_path": "%s/%s/scenario/first.ks" % (resource_code, resource_directory),
                        "title": scene['title'],
                        "summary": scene['description'],
                        "resource_directory": resource_directory
                    }
            else:
                scene_info = {
                    "scenario_path": "%s/%s/scenario.json" % (resource_code, resource_directory),
                    "resource_directory": resource_directory
                }

            ep_infos[file_name] = scene_info

    if name == None:
        name = character_name
        path = os.path.join(data_directory, "kamihime_" + rarity, name)
        if not os.path.exists(path):
            os.mkdir(os.path.join(data_directory, "kamihime_" + rarity, name))

    # Write to folder
    for file_name in ep_infos:
        save_script("kamihime_" + rarity, name, file_name + '.json', ep_infos[file_name])


############################################################################
# EIDOLON FUNCTIONS
############################################################################
def download_eidolon_episodes_info(info):
    url = base_url['eidolon']['scenes'] + str(info['summon_id'])
    r = s.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        info_ep_1 = json.loads(r.text)
        ep_1_id = int(info_ep_1['episode_id'].split('_')[0])
        eps = [ep_1_id - 1, ep_1_id]
        
        scenes = info['episodes']
        ep_0_title = scenes[0]['title']
        del scenes[:]
        for ep in eps:
            r = s.get(base_url['episode'] + str(ep) + "_harem-summon", headers=headers, verify=False)
            data = json.loads(r.text)
            scenario = data['chapters'][0]['scenarios'][0]
            scenes.append({
                "id": scenario['scenario_id'],
                "resource_directory": scenario['resource_directory'],
                "title": info_ep_1['title'] if eps.index(ep) == 1 else ep_0_title if eps.index(ep) == 0 else "No data",
                "description": "No data" if eps.index(ep) <> 1 else info_ep_1['description']
            })

            if data['chapters'][0].has_key('harem_scenes'):
                harem_scene = data['chapters'][0]['harem_scenes'][0]
                scenes.append({
                    "id": harem_scene['harem_scene_id'],
                    "resource_directory": harem_scene['resource_directory']
                })
        
        info['episodes'] = scenes
        save_info(eid_info_folder, str(info['summon_id']) + '.json', info)
    else:
        print_console('Unable to download: %s' % url)
        logging.error('Error: %s - url: %s' % (r.status_code, url))

    return info


def download_eidolon_script(info):
    character_name = info['name']

    if not info.has_key('episodes') or len(info['episodes']) < 3:
        info = download_eidolon_episodes_info(info)
    
    # Check available scenes
    scenes = info['episodes']
    ep_infos = dict()
    name = None

    for scene in scenes:
        file_name = scene['id']
        resource_directory = scene['resource_directory']

        if episodes.has_key(file_name):
            name = episodes[file_name]
        else:
            resource_code = '/'.join([resource_directory[-4:][i:i+2] for i in range(0, len(resource_directory[-4:]), 2)])
            scene_idx = scenes.index(scene)
            if scene_idx in [0, 1]:
                url = base_url['scene'] + file_name
                r = s.get(url, headers=headers, verify=False)
                if r.status_code == 200:
                    scene_info = json.loads(r.text)
                else:
                    scene_info = {
                        "scenario_path": "%s/%s/scenario/first.ks" % (resource_code, resource_directory),
                        "title": scene['title'],
                        "summary": scene['description'],
                        "resource_directory": resource_directory
                    }
            else:
                scene_info = {
                    "scenario_path": "%s/%s/scenario.json" % (resource_code, resource_directory),
                    "resource_directory": resource_directory
                }

            ep_infos[file_name] = scene_info

    if name == None:
        name = character_name
        path = os.path.join(data_directory, "eidolon", name)
        if not os.path.exists(path):
            os.mkdir(os.path.join(data_directory, "eidolon", name))

    # Write to folder
    for file_name in ep_infos:
        save_script("eidolon", name, file_name + '.json', ep_infos[file_name])


def download_soul_info(soul_info):
    job_id = soul_info['job_id']
    if ('%s.json' % job_id) not in soul_list:
        info = download_soul_episodes_info(soul_info)
    else:
        info = load_info(soul_info_folder, str(job_id))
    download_soul_script(info)
    return


def download_kamihime_info(kh_id):
    if (kh_id + '.json') not in kh_list:
        url = base_url['kamihime']['info'] + kh_id
        info = download_info(kh_id, url, kh_info_folder)
    else:
        print_console('%s already exists' % (kh_id + '.json'))
        info = load_info(kh_info_folder, kh_id)
    
    if info == None:
        return
    else:
        download_kamihime_script(info)


def download_eidolon_info(eid_id):
    if (eid_id + '.json') not in eid_list:
        url = base_url['eidolon']['info'] + eid_id
        info = download_info(eid_id, url, eid_info_folder)
    else:
        print_console('%s already exists' % (eid_id + '.json'))
        info = load_info(eid_info_folder, eid_id)

    if info == None:
        return
    else:
        download_eidolon_script(info)


############################################################################
# MAIN ENTRY
############################################################################
soul_list = set(os.listdir(soul_info_folder))
print_console('Download soul info...')
soul_infos = download_souls_info()

with cf.ThreadPoolExecutor(max_workers=thread_num) as executor:
    futures = [executor.submit(download_soul_info, soul_info) for soul_info in soul_infos]

    for _ in cf.as_completed(futures):
        pass


kh_list = set(os.listdir(kh_info_folder))
kh_ids = []
print_console('Download kamihime info...')
for x in (0, 5, 6, 7):
    for y in xrange(200):
        kh_ids.append(str(x*1000 + y + 1))

with cf.ThreadPoolExecutor(max_workers=thread_num) as executor:
    futures = [executor.submit(download_kamihime_info, kh_id) for kh_id in kh_ids]

    for _ in cf.as_completed(futures):
        pass
        

eid_list = set(os.listdir(eid_info_folder))
eid_ids = []
print_console('Download eidolon info...')
for idx in ((0, 1), (0.011, 35), (0.216, 6), (2, 10), (5, 50), (6, 200), (9.05, 10), (9.2, 20)):
    x = idx[0]
    for y in xrange(idx[1]):
        eid_ids.append(str(int(x*1000 + y + 1)))

with cf.ThreadPoolExecutor(max_workers=thread_num) as executor:
    futures = [executor.submit(download_eidolon_info, eid_id) for eid_id in eid_ids]

    for _ in cf.as_completed(futures):
        pass
