# -*- coding: utf-8 -*-
import json
import os
import sys
import codecs
import io
import logging
logging.basicConfig(
    filename='2_error.log',
    filemode='w',
    level='INFO',
    format='[%(levelname)s] %(asctime)s: %(message)s'
)

asset_folder = 'assets'

def cmd(line):
    return '    '+line

def print_console(text):
    try:
        print text
    except:
        pass

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
    line = line.replace(u'{{主人公}}', player_name)
    return line
  
# player_name = 'Master'

print "Player's name: ",
player_name = raw_input().decode(sys.stdin.encoding).strip()

data_directory = 'raw_scenario'
dst_folder = 'scenario'
# data_directory = 'nutaku/raw_scenario'
# dst_folder = 'nutaku/scenario'

if not os.path.exists(dst_folder):
    os.mkdir(dst_folder)

character_types = os.listdir(data_directory)

dmm_scenarios = []

for character_type in character_types:
    lst = os.listdir(os.path.join(data_directory, character_type).decode('utf8'))
    for character in lst:
        print_console(character)

        scenarios = os.listdir(os.path.join(data_directory, character_type, character))

        for filename in scenarios:
            with open(os.path.join(data_directory, character_type, character, filename)) as file:
                data = json.loads(file.read().replace(
                    '&nbsp;', '_').replace('\\u00a0', '_'))

            story_type = character_type.split('_')[0]
            name = character

            label = 'story_nutaku_' + story_type + '_' + \
                "%03d" % int(filename.split('_')[0])
            script = ['label %s:' % label]
            chara = {}
            name = '   '

            # print label

            rd = data['resource_directory']

            if data.has_key('scene_data'):
                dmm_scenarios.append(
                    dict(character=character, filename=filename, rd=rd))

            if data.has_key('scenario'):
                # print data
                data = data['scenario'].replace('"][', '"]\n[').split('\n')
                for command in data:
                    if command.startswith('*') or command.startswith('#') or command.startswith('Tap to continue'):
                        continue
                    if command.startswith('['):
                        endIdx = command.rfind(']')
                        command = command[1:endIdx].replace(
                            '[', '(').replace(']', ')').replace('"', '').split()
                        if len(command) < 2:
                            continue
                        line = dict(cmd=command[0])
                        for arg in command[1:]:
                            tmp = arg.split('=')
                            if len(tmp) == 2:
                                line[tmp[0]] = tmp[1]

                        if filename == '5009_harem-character.json' and line.has_key('name') and line['name'] == 'sukunahikona':
                            # Hot fix for [Masterpiece] Hermes 5009_harem-character.json
                            line['name'] = 'herumesu2nd'

                        # print line
                        if line['cmd'].startswith('chara_new'):
                            chara[line['name']] = dict(
                                name=line['jname'].replace('_', ' '))
                        if line['cmd'].startswith('chara_face'):
                            if not chara[line['name']].has_key('face'):
                                chara[line['name']]['face'] = dict()
                            chara[line['name']]['face'][line['face']
                                                        ] = line['storage']

                        if line['cmd'].startswith('playbgm'):
                            if exists_in_assets(line['storage']):
                                script.append(
                                    cmd('play music "nutaku/assets/%s"' % (line['storage'])))

                        if line['cmd'].startswith('bg'):
                            c = 'show expression ' + \
                                '(Frame("nutaku/assets/%s"))' % (line['storage']
                                                        ) + ' as bg behind char with dissolve'
                            script.append(cmd(c))

                        if line['cmd'].startswith('chara_show'):                            
                            name = chara[line['name']]['name']

                        if line['cmd'].startswith('chara_mod'):
                            sprite = chara[line['name']]['face'][line['face']]
                            if '.png' not in sprite:
                                continue
                            c = 'show expression ' + \
                                '(im.Scale("nutaku/assets/%s",config.screen_height,config.screen_height))' % (
                                    sprite) + ' as char with dissolve'
                            script.append(cmd(c))

                        if line['cmd'].startswith('playse'):
                            if exists(rd, line['storage']):
                                script.append(
                                    cmd('voice ' + '"nutaku/assets/%s/' % rd + line['storage'])+'"')

                        if line['cmd'].startswith('chara_hide'):
                            script.append(cmd('hide char with dissolve'))
                            name = '   '

                    elif not command.startswith(';layer') and not command.startswith(u';画面'):
                        text = command.replace('"', "'").replace('%', '\\%')
                        text = text.replace('[l]', '').replace(
                            '[r]', '').replace('[cm]', '')
                        text = text.replace('%', '%%')
                        text = text.replace('\n', '').replace('\r', '')
                        if len(text.replace(' ', '')) < 2:
                            continue
                        # print text
                        text = player_name_unification(text)
                        script.append(cmd('"%s" "%s"' % (name, text)))

            elif data.has_key('scene_data'):
                transition = 'dissolve'
                for entry in data['scene_data']:
                    if entry.has_key('bgm'):
                        if exists(rd, entry['bgm']):
                            script.append(
                                cmd('play music "nutaku/assets/%s"' % (entry['bgm'])))
                        else:
                            script.append(cmd('play music "nutaku/assets/bgm_h_003.mp3"'))

                    if entry.has_key('film'):
                        if entry['film'].startswith('pink'):
                            continue
                        fps = float(entry['fps'])
                        if fps > 1:
                            c = 'show expression '
                            c += '(Zoomable(Frame(anim.Filmstrip(im.Rotozoom("nutaku/assets/%s/%s",90,1.0),(900,640),(16,1),%f)))) ' % (
                                rd, entry['film'], 1/fps)
                            c += 'at top as cg with dissolve'
                            script.append(cmd(c))
                        else:
                            c = 'show expression '
                            c += '(Zoomable(Frame(im.Rotozoom("nutaku/assets/%s/%s",90,1.0)))) ' % (
                                rd, entry['film'])
                            c += 'at top as cg with dissolve'
                            script.append(cmd(c))

                    for line in entry['talk']:
                        if line.has_key('voice'):
                            if len(line['voice']):
                                if exists(rd, line['voice']):
                                    script.append(
                                        cmd('voice ' + '"nutaku/assets/%s/' % rd + line['voice'])+'"')
                        else:
                            script.append(cmd('voice sustain'))

                        if not line.has_key('words') or not len(line['words']):
                            line['chara'] = '   '
                            line['words'] = '{i}click to proceed'

                        line['words'] = line['words'].replace(
                            '[', '').replace(']', '').replace('"', '')
                        line['words'] = line['words'].replace('%', '%%')
                        line['words'] = line['words'].replace(
                            '\n', '').replace('\r', '')
                        line['words'] = player_name_unification(line['words'])
                        script.append(cmd('"%s" "%s"' % (line['chara'].replace('"', "'").replace(
                            '%', '\\%').replace('[', '(').replace(']', ')'), line['words'])))

            script.append(cmd("hide char with dissolve"))
            script.append(cmd("hide cg with dissolve"))
            script.append(cmd("hide bg with dissolve"))
            script.append(cmd("stop music"))
            script.append(cmd("jump index"))

            if not os.path.exists(dst_folder):
                os.mkdir(dst_folder)

            # with codecs.open('test.rpy', 'w', 'utf-8') as file:
            with codecs.open(os.path.join(dst_folder, '%s.rpy' % label), 'w', 'utf-8') as file:
                for line in script:
                    file.write(line)
                    file.write('\n')
