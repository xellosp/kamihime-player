# -*- coding: utf-8 -*-
import codecs
import io
import json
import os
import re
import sys
import traceback
import logging
logging.basicConfig(
    filename='2_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

data_directory = 'raw_scenario'
dst_folder = 'scenario'
asset_folder = 'assets'
# data_directory = 'dmm/raw_scenario'
# dst_folder = 'dmm/scenario'
# asset_folder = 'dmm/assets'

if not os.path.exists(dst_folder):
    os.mkdir(dst_folder)

print u'キャラの名前: ',
player_name = raw_input().decode(sys.stdin.encoding).strip()

def cmd(line):
    return '    ' + line


def exists_in_assets(file):
    file_path = os.path.join(asset_folder, file)
    if os.path.exists(file_path):
        return True
    else:
        #print '%s not exists' % file_path
        logging.error('%s not exists' % file_path)
        return False


def exists(rd, file):
    file_path = os.path.join(asset_folder, rd, file)
    if os.path.exists(file_path):
        return True
    else:
        #print '%s not exists' % file_path
        logging.error('%s not exists' % file_path)
        return False


def player_name_unification(line):
    if player_name:
        return line.replace(u'{{主人公}}', player_name)
    else:
        return line


def parse_h_scene(data, script, rd):
    for entry in data:
        if entry.has_key('bgm'):
            if exists_in_assets(entry['bgm']):
                script.append(cmd('play music "dmm/%s/%s"' %
                                  (asset_folder, entry['bgm'])))
        if exists(rd, entry['film']):
            if entry['fps'] > 1:
                fps = entry['fps']
                c = 'show expression '
                c += '(Zoomable(Frame(anim.Filmstrip(im.Rotozoom("dmm/%s/%s/%s",90,1.0),(900,640),(16,1),%f)))) ' % (
                    asset_folder, rd, entry['film'], 1.0/fps)
                c += 'at top as cg with dissolve'
                script.append(cmd(c))
            else:
                c = 'show expression '
                c += '(Zoomable(Frame(im.Rotozoom("dmm/%s/%s/%s",90,1.0)))) ' % (
                    asset_folder, rd, entry['film'])
                c += 'at top as cg with dissolve'
                script.append(cmd(c))
        for line in entry['talk']:
            if line.has_key('voice'):
                if len(line['voice']):
                    if exists(rd, line['voice']):
                        script.append(cmd('voice ' + '"dmm/%s/%s/%s"' %
                                          (asset_folder, rd, line['voice'])))
            else:
                script.append(cmd('voice sustain'))

            if not len(line['words']):
                line['chara'] = '   '
                line['words'] = '{i}click to proceed'

            line['words'] = line['words'].replace(
                '[', '').replace(']', '').replace('"', '')
            line['words'] = line['words'].replace('%', '%%')
            line['words'] = line['words'].replace('\n', '').replace('\r', '')
            line['words'] = player_name_unification(line['words'])
            script.append(cmd('"%s" "%s"' % (line['chara'].replace('"', "'").replace('%', '\\%').replace('[', '(').replace(']', ')'), line['words'])))

    script.append(cmd("hide char with dissolve"))
    script.append(cmd("hide cg with dissolve"))
    script.append(cmd("hide bg with dissolve"))
    script.append(cmd("stop music"))
    script.append(cmd("jump index"))
    return script


def parse_scenario(data, script, rd):
    chara_info = {}
    chara_name = ''
    for line in data.split('\n'):
        try:
            if line.startswith('[chara_new'):
                name, jname = re.findall(r'name="(.*?)" .* jname="(.*?)"', line)[0]
                chara_info[name] = {}
                chara_info[name]['jname'] = jname
                chara_info[name]['face'] = {}
            elif line.startswith('[chara_face'):
                name, face, storage = re.findall(
                    r'name="(.*?)" face="(.*?)" storage="(.*?)"', line)[0]
                chara_info[name]['face'][face] = storage
            elif line.startswith('[playbgm'):
                bgm = re.findall(r'storage="(.*?)"', line)[0]
                script.append(cmd('play music "dmm/%s/%s"' % (asset_folder, bgm)))
            elif line.startswith('[bg'):
                bg = re.findall(r'storage="(.*?)"', line)[0]
                script.append(cmd('show expression ' + '(Frame("dmm/%s/%s"))' %
                                (asset_folder, bg) + ' as bg behind char with dissolve'))
            elif line.startswith('[chara_show'):
                chara_name = chara_info[re.findall(
                    r'name="(.*?)"', line)[0]]['jname']
            elif line.startswith('[chara_mod'):
                name, face = re.findall(r'name="(.*?)" face="(.*?)"', line)[0]
                sprite = chara_info[name]['face'][face]
                script.append(cmd('show expression ' + '(im.Scale("dmm/%s/%s",config.screen_height,config.screen_height))' %
                                (asset_folder, sprite) + ' as char with dissolve'))
            elif line.startswith('[playse'):
                se = re.findall(r'storage="(.*?)"', line)[0]
                if exists(rd, se):
                    script.append(cmd('voice ' + '"dmm/%s/%s/%s"' %
                                    (asset_folder, rd, se)))
            elif line.startswith('[chara_hide'):
                script.append(cmd('hide char with dissolve'))
                chara_name = ''
            elif line.startswith('*') or line.startswith('#') or line.startswith('Tap to continue') or line.startswith('['):
                continue
            elif not line.startswith(';layer') and not line.startswith(u';画面'):
                text = line.strip().replace('"', "'").replace('%', '\\%')
                text = re.sub('\[.*?\]', '', text)
                text = text.replace('%', '%%')
                text = text.replace('\n', '').replace('\r', '')
                text = player_name_unification(text)
                script.append(cmd('"%s" "%s"' % (chara_name, text)))
        except:
            logging.error(traceback.format_exc())

    script.append(cmd("hide char with dissolve"))
    script.append(cmd("hide cg with dissolve"))
    script.append(cmd("hide bg with dissolve"))
    script.append(cmd("stop music"))
    script.append(cmd("jump index"))
    return script


# ---------------------------------------Start-------------------------------------------
for type in os.listdir(data_directory):
    for character in os.listdir(os.path.join(data_directory, type)):
        print character

        scenarios = os.listdir(os.path.join(data_directory, type, character))

        for filename in scenarios:
            if filename.endswith('_script.ks') or filename.endswith('_script.json'):
                continue

            with open(os.path.join(data_directory, type, character, filename)) as file:
                data = json.load(file)

            story_type = type.split('_')[0]
            name = character

            label = 'story_dmm_' + story_type + '_' + \
                "%03d" % int(filename.split('_')[0])
            script = ['label %s:' % label]

            print label

            rd = data['resource_directory']
            if data['scenario_path'].endswith('.ks'):
                script_file = os.path.join(data_directory, type, character, filename.replace('.json', '') + '_script.ks')
                if os.path.exists(script_file):
                    with open(script_file) as file:
                        script = parse_scenario(
                            file.read().decode('utf-8'), script, rd)
                else:
                    print 'Error: %s script file not exists' % filename
                    logging.error('%s script file not exists' % filename)
            else:
                script_file = os.path.join(data_directory, type, character, filename.replace('.json', '') + '_script.json')
                if os.path.exists(script_file):
                    with open(script_file) as file:
                        script = parse_h_scene(json.load(file), script, rd)
                else:
                    print 'Error: %s script file not exists' % filename
                    logging.error('%s script file not exists' % filename)

            with codecs.open(os.path.join(dst_folder, '%s.rpy' % label), 'w', 'utf-8') as file:
                for line in script:
                    try:
                        file.write(line)
                        file.write('\n')
                    except:
                        print 'Error: %s' % line
                        traceback.print_exc()
                        logging.error('Error: %s' % line)
                        break
