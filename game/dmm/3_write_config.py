import json
import os
import sys
import codecs
import logging
from listing import UnicodeConfigParser
logging.basicConfig(
    filename='3_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

parser = UnicodeConfigParser()

info = dict(kamihime={}, eidolon={}, soul={}, story={})
eid_mapper = {46: 6001, 223: 6002, 15: 6003, 24: 6004, 33: 6005, 8: 6006, 48: 6007,
              259: 6008, 239: 6009, 37: 5001, 32: 5002, 10: 5003, 28: 5004, 14: 5005, 9051: 6020}
kh_mapper = {4: 5001, 14: 5002, 41: 5003, 9: 5004, 91: 5005, 8: 5006, 15: 5007, 25: 5008, 112: 5009, 57: 5010,
             22: 6001, 97: 6002, 72: 6003, 95: 6004, 80: 6005, 29: 6006, 58: 6007, 62: 6008, 23: 6009, 113: 6010, 60: 6011, 107: 6012,
             96: 7001, 98: 7002, 99: 7003, 81: 7004, 100: 7005, 85: 7006, 93: 7007, 114: 7008, 102: 7009}

eid_info_folder = 'info_eidolon'
kh_info_folder = 'info_kamihime'
soul_info_folder = 'info_soul'
main_quest_info_folder = 'main_quests'
config_file = 'config.ini'
data_folder = 'raw_scenario'

# eid_info_folder = 'dmm/info_eidolon'
# kh_info_folder = 'dmm/info_kamihime'
# soul_info_folder = 'dmm/info_soul'
# main_quest_info_folder = 'dmm/main_quests'
# config_file = 'dmm/config.ini'
# data_folder = 'dmm/raw_scenario'

def log_console(text):
    try:
        print text
    except:
        None

def get_character_info(entry, scenario, type):
    script_file = os.path.join(data_folder, type, entry, scenario.replace('.json', '') + '_script.json')
    story_type = type.split('_')[0]
    try:
        with open(script_file) as file:
            data = json.load(file)
            if story_type == 'story':
                stage, level = data[-1]['film'].split('-')[0:2]
                if int(stage) == 0:
                    if entry == '1':
                        index = 100001
                    else:
                        index = 100002
                else:
                    index = (int(stage) - 1) * 5 + int(level)
            else:
                index = int(data[-1]['film'].split('-')[0])
                if story_type == 'eidolon':
                    if eid_mapper.has_key(index) and entry.find('Lilim') == -1:
                        index = eid_mapper[index]
                elif story_type == 'kamihime':
                    if kh_mapper.has_key(index):
                        index = kh_mapper[index]
            try:
                return info[story_type].pop(index)
            except:
                print '%s.json not found' % index
                logging.error('%s.json not found' % index)
                return None
    except:
        print '%s not found' % script_file
        logging.error('%s not found' % script_file)
        return None


def get_scenario_index(scenario, stories, hcenes):
    scene = scenario.replace('.json', '').replace('.ks', '')
    try:
        index = stories.index(scene + '_script.ks') + 1
        if index == 3:
            index = 4
    except:
        try:
            index = hcenes.index(scene + '_script.json')
            if index == 0:
                index = 3
            else:
                index = 5
        except:
            print 'Missing script file for %s' % scene
            logging.error('Missing script file for %s' % scene)
            sys.exit()
    return index


lst = os.listdir(eid_info_folder)
for entry in lst:
    # print entry
    with open(os.path.join(eid_info_folder, entry)) as file:
        data = json.load(file)
        if data['has_harem'] == True:
            id = data['summon_id']
            info['eidolon'][id] = dict()
            info['eidolon'][id]['description'] = data['description']
            info['eidolon'][id]['name'] = data['name']
            info['eidolon'][id]['rare'] = data['rare']

lst = os.listdir(kh_info_folder)
for entry in lst:
    # print entry
    with open(os.path.join(kh_info_folder, entry)) as file:
        data = json.load(file)
        id = data['character_id']
        info['kamihime'][id] = dict()
        info['kamihime'][id]['description'] = data['description']
        info['kamihime'][id]['name'] = data['name']
        info['kamihime'][id]['rare'] = data['rare']

lst = os.listdir(soul_info_folder)
for character in lst:
    # print entry
    with open(os.path.join(soul_info_folder, character)) as file:
        data = json.load(file)
        for record in data['data']:
            id = record['job_id']
            info['soul'][id] = dict()
            info['soul'][id]['description'] = record['description']
            info['soul'][id]['name'] = record['name']

lst = os.listdir(main_quest_info_folder)
for character in lst:
    with open(os.path.join(main_quest_info_folder, character)) as file:
        data = json.load(file)
        for record in data['data']:
            id = record['quest_id']
            if id == 100001 and record['battle_no'] == 2:
                id = 100002
            info['story'][id] = dict()
            info['story'][id]['description'] = record['description']

for type in os.listdir(data_folder):
    for entry in os.listdir(os.path.join(data_folder, type)):
        print entry

        scenarios = os.listdir(os.path.join(data_folder, type, entry))
        stories = [scenario for scenario in scenarios if scenario.endswith('_script.ks')]
        hcenes = [scenario for scenario in scenarios if scenario.endswith('_script.json')]
        stories.sort(key=lambda id: int(id.split('_')[0]))
        hcenes.sort(key=lambda id: int(id.split('_')[0]))
        scenarios = [scenario for scenario in scenarios if not scenario.endswith(
            '_script.json') and not scenario.endswith('_script.ks')]

        story_type = type.split('_')[0]
        name = entry
        chara_info = None

        if story_type == 'kamihime' and len(scenarios) > 5:
            print entry, 'should be 5 or less files in folder'
            logging.error('should be 5 or less files in folder %s' % entry)
            sys.exit()
        elif story_type == 'eidolon' and len(scenarios) > 3:
            print entry, 'should be 3 or less files in folder'
            logging.error('should be 3 or less files in folder %s' % entry)
            sys.exit()

        for scenario in scenarios:
            with open(os.path.join(data_folder, type, entry, scenario)) as file:
                data = json.load(file)

            id = int(scenario.split('_')[0])
            label = 'story_dmm_' + story_type + '_' + "%03d" % id

            if story_type == 'story':
                section_name = 'story_%s' % name
            else:
                section_name = name.replace('[', '(').replace(']', ')')

            if not parser.has_section(section_name):
                parser.add_section(section_name)

            scene_index = get_scenario_index(scenario, stories, hcenes)
            if story_type == 'story' and scene_index == 3:
                scene_index = 2

            if data.has_key('title'):  # ks file
                parser.set(section_name, 'title_%d' % scene_index,
                           data['title'].replace('[', '(').replace(']', ')'))
                parser.set(section_name, 'summary_%d' % scene_index,
                           data['summary'].replace('[', '(').replace(']', ')'))
            else:  # json file
                if chara_info == None:
                    chara_info = get_character_info(entry, scenario, type)

            parser.set(section_name, 'scene_%d' % scene_index, label)

        if chara_info is not None:
            if story_type == 'story':
                parser.set(section_name, 'name', section_name)
            else:
                parser.set(section_name, 'name', chara_info['name'].replace('[', '(').replace(']', ')'))
            
            if story_type == 'kamihime':
                parser.set(section_name, 'type', story_type + '_' + chara_info['rare'])
            else:
                parser.set(section_name, 'type', story_type)
            parser.set(section_name, 'description', chara_info['description'])

        else:
            parser.set(section_name, 'name', name.replace('[', '(').replace(']', ')'))
            parser.set(section_name, 'type', type)

info.pop('story')
for story_type in info:
    for index in info[story_type]:
        chara_info = info[story_type][index]
        section_name = chara_info['name'].replace('[', '(').replace(']', ')')
        log_console(section_name)

        if not parser.has_section(section_name):
            parser.add_section(section_name)

        parser.set(section_name, 'name', section_name)

        if story_type == 'kamihime':
            parser.set(section_name, 'type', story_type + '_' + chara_info['rare'])
        else:
            parser.set(section_name, 'type', story_type)

        parser.set(section_name, 'description', chara_info['description'])

with codecs.open(config_file, 'w', 'utf-8') as file:
    parser.write(file)
