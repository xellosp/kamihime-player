define black = Solid((0,0,0,255))

################################################################################
## Game Persistent Variables
################################################################################
default persistent.bg_index = -1
default persistent.bgm_index = -1

init python:
    config.keymap['rollback'].remove('mousedown_4')
    config.keymap['game_menu'].remove('mouseup_3')
    config.developer = False
    config.log = 'logtest.log'

screen main_menu:
    tag main_menu
    add(Frame("backgrounds/%s"%(bg[persistent.bg_index])))

    vbox xalign 0.5 yalign 0.7 spacing 20 xsize 250:
        if nutaku_exist == True:
            imagebutton auto "gui/button/nutaku-%s.png" action Return(['index', 'nutaku'])
        if dmm_exist == True:
            imagebutton auto "gui/button/dmm-%s.png" action Return(['index', 'dmm'])
        frame background "gui/button/background-idle.png" xsize 250 ysize 50:
            hbox xsize 250 ysize 50:
                imagebutton auto "gui/button/left_arrow-%s.png" xalign 0.0 yalign 0.3 action SetField(persistent, "bg_index", (persistent.bg_index + 1) % len(bg))
                imagebutton auto "gui/button/right_arrow-%s.png" xalign 0.9 yalign 0.3 action SetField(persistent, "bg_index", (persistent.bg_index - 1) % len(bg))
        frame background "gui/button/bgm-idle.png" xsize 250 ysize 50:
            hbox xsize 250 ysize 50:
                imagebutton auto "gui/button/left_arrow-%s.png" action [mr.Previous(), SetField(persistent, "bgm_index", (persistent.bgm_index - 1) % len(bgm))] xalign 0.0 yalign 0.3
                imagebutton auto "gui/button/right_arrow-%s.png" action [mr.Next(), SetField(persistent, "bgm_index", (persistent.bgm_index + 1) % len(bgm))] xalign 0.9 yalign 0.3
        if (config.screen_width == 1280) and (config.screen_height == 720):
            imagebutton auto "gui/button/res_16_9-%s.png" action [SetField(config, "screen_width", 1080), SetField(config, "screen_height", 720), 
            SetField(persistent, "default_width", 1080), SetField(persistent, "default_height", 720),
            SetVariable("x_ratio", 1080.0/1280.0), SetVariable("y_ratio", 1.0),
            Preference("display", (1280, 720)), Preference("display", "fullscreen") if _preferences.fullscreen == True else None]
        else:
            imagebutton auto "gui/button/res_3_2-%s.png" action [SetField(config, "screen_width", 1280), SetField(config, "screen_height", 720), 
            SetField(persistent, "default_width", 1280), SetField(persistent, "default_height", 720),
            SetVariable("x_ratio", 1.0), SetVariable("y_ratio", 1.0),
            Preference("display", (1280, 720)), Preference("display", "fullscreen") if _preferences.fullscreen == True else None]
        imagebutton auto "gui/button/exit-%s.png" action Return('exit')

    if not renpy.music.is_playing():
        on "show" action [mr.SetSingleTrack(True), mr.SetLoop(True), mr.Play("bgm/%s"%bgm[persistent.bgm_index])]


screen index:
    tag index
    add(Frame("backgrounds/%s"%(bg[persistent.bg_index])))

    vbox xfill True spacing 10:
        hbox xfill True:
            imagebutton auto "gui/button/back-%s.png" align(0.0, 0.0) action Return(["back", "main_menu"])
            #-------------------------------------------------CATEGORY SELECT---------------------------------------------------------------
            vbox xfill True spacing 10:
                hbox xalign 0.5 spacing 20:
                    # if selected_platform == 'nutaku':
                    if selected_category == 'story':
                        imagebutton idle "gui/button/story-hover.png" action SetVariable('selected_category', '')
                    else:
                        imagebutton idle "gui/button/story-idle.png" action SetVariable('selected_category', 'story')
                    if 'kamihime' in selected_category:
                        imagebutton idle "gui/button/kamihime-hover.png" action SetVariable('selected_category', '')
                    else:
                        imagebutton idle "gui/button/kamihime-idle.png" action SetVariable('selected_category', 'kamihime_R')
                    if selected_category == 'eidolon':
                        imagebutton idle "gui/button/eidolon-hover.png" action SetVariable('selected_category', '')
                    else:
                        imagebutton idle "gui/button/eidolon-idle.png" action SetVariable('selected_category', 'eidolon')
                    # if selected_platform == 'nutaku':
                    if selected_category == 'soul':
                        imagebutton idle "gui/button/soul-hover.png" action SetVariable('selected_category', '')
                    else:
                        imagebutton idle "gui/button/soul-idle.png" action SetVariable('selected_category', 'soul')
                if 'kamihime' in selected_category:
                    hbox xalign 0.5 spacing 20:
                        if selected_category == 'kamihime_R':
                            imagebutton idle "gui/button/rare-hover.png" action SetVariable('selected_category', 'kamihime_R')
                        else:
                            imagebutton idle "gui/button/rare-idle.png" action SetVariable('selected_category', 'kamihime_R')
                        if selected_category == 'kamihime_SR':
                            imagebutton idle "gui/button/sr-hover.png" action SetVariable('selected_category', 'kamihime_SR')
                        else:
                            imagebutton idle "gui/button/sr-idle.png" action SetVariable('selected_category', 'kamihime_SR')
                        if selected_category == 'kamihime_SSR':
                            imagebutton idle "gui/button/ssr-hover.png" action SetVariable('selected_category', 'kamihime_SSR')
                        else:
                            imagebutton idle "gui/button/ssr-idle.png" action SetVariable('selected_category', 'kamihime_SSR')

        #-------------------------------------------------GRID---------------------------------------------------------------
        if selected_category == 'story':
            $renpy.log("x: %s"%x_ratio)
            $renpy.log("y: %s"%y_ratio)
            vbox ymaximum (config.screen_height - 55) xfill True:
                vpgrid:
                    cols 2
                    spacing int(10*x_ratio)
                    draggable True
                    mousewheel True

                    scrollbars "vertical"
                    side_xalign 0.5
                    xfill True

                    for char in chars[selected_category]:
                        frame align(0.5,0.5) background Solid((57,48,41,200)):
                            vbox xysize(int(610*x_ratio),int(230*x_ratio)) align(0.5,0.5):
                                frame ysize int(40*x_ratio) xfill True background Solid((206,190,174,200)):
                                    text "{color=#222}{size=-1}%s.%s"%(char.split('_')[1], data[char]['title_1']) align(0.5,0.5)
                                hbox align(0.5,0.5) spacing 10:
                                    if renpy.exists('%s/story_thumb/%s.jpg'%(selected_platform, char)):
                                        add im.Scale('%s/story_thumb/%s.jpg'%(selected_platform, char),int(200*x_ratio),int(200*x_ratio))
                                    else:
                                        add im.Scale('%s/story_thumb/blank.png'%selected_platform,int(200*x_ratio),int(200*x_ratio))
                                    vbox ymaximum int(148*x_ratio) xfill True spacing 10:
                                        viewport id 'vp6':
                                            child_size(int(380*x_ratio),10000)
                                            draggable True
                                            mousewheel True
                                            text "{color=#fff}{size=-3}%s"%data[char]['summary_1'] align(0.5,0.5)
                                        hbox align(0.5,0.5) spacing 10:
                                            frame align(0.5,0.5) xsize int(180*x_ratio):
                                                textbutton ("{size=-2}Run intro") ysize int(40*x_ratio) align(0.5,0.5) action Return(['run',data[char]['scene_1']])
                                            frame align(0.5,0.5) xsize int(180*x_ratio):
                                                textbutton ("{size=-2}Run hscene") ysize int(40*x_ratio) align(0.5,0.5) action Return(['run',data[char]['scene_2']])
        elif selected_category != '':
            vbox ymaximum (config.screen_height - 55) xalign 0.5:
                vpgrid:
                    if config.screen_width == 1280:
                        cols 6
                    else:
                        cols 5
                    spacing 5
                    draggable True
                    mousewheel True

                    scrollbars "vertical"
                    side_xalign 0.5
                    for char in chars[selected_category]:
                        $char_name = data[char]['name']
                        frame xysize(205,230) align(0.5,0.5) background Frame('gui/portrait_bg.png'):
                            if renpy.exists(data[char]['portrait']):
                                vbox ypos 5:
                                    imagebutton idle im.Scale(data[char]['portrait'], 195, 190) action Return(['info',char])
                                    frame xfill True ysize 25 background Solid(data[char]['color']):
                                        if len(char_name) > 16:
                                            text ("{size=-15}{color=#eee}%s"%char_name) align(0.5,0.5)
                                        elif len(char_name) > 9:
                                            text ("{size=-11}{color=#eee}%s"%char_name) align(0.5,0.5)
                                        else:
                                            text ("{size=-6}{color=#eee}%s"%char_name) align(0.5,0.5)
                            else:
                                frame background Solid(data[char]['color']) align(0.5,0.5) xfill True:
                                    if len(char_name) > 16:
                                            textbutton ("{size=-15}{color=#eee}%s"%char_name) align(0.5,0.5) action Return(['info', char])
                                    elif len(char_name) > 9:
                                        textbutton ("{size=-11}{color=#eee}%s"%char_name) align(0.5,0.5) action Return(['info', char])
                                    else:
                                        textbutton ("{size=-6}{color=#eee}%s"%char_name) align(0.5,0.5) action Return(['info', char])

    if not renpy.music.is_playing():
        on "show" action mr.Play("bgm/%s"%bgm[persistent.bgm_index])


screen info:
    tag info
    add(Frame("backgrounds/%s"%(bg[persistent.bg_index])))
    add(im.Scale(data[selected_character]['full_art'], 960*x_ratio, 640*x_ratio)) align(1.3,1.0)
    imagebutton auto "gui/button/back-%s.png" align(0.0, 0.0) action Return(['back', 'index'])
        
    $c = selected_character
    $char_name = data[c]['name']

    vbox ypos 60 xalign 0.01 spacing 5:
        vbox xysize(500,150):
            if data.has_key(c):
                frame background Solid((255,255,255,150)) ysize 40 xfill True:
                    if len(data[c]['name']) > 40:
                        text "{color=#000}{size=-5}%s"%data[c]['name'] align(0.5,0.5)
                    else:
                        text "{color=#000}%s"%data[c]['name'] align(0.5,0.5)
                frame background Solid((0,0,0,150)) xfill True:
                    vbox:
                        viewport id 'vp1':
                            child_size(480,10000)
                            xpos 10
                            draggable True
                            mousewheel True
                            if data[c].has_key('description'):
                                text "{color=#fff}{size=-2}%s"%data[c]['description'] align(0.5,0.5)
                            else:
                                text "{color=#fff}No data" align(0.5,0.5)
            else:
                frame background Solid((0,0,0,150)) xfill True yfill True:
                    text "{color=#fff}No data" align(0.5,0.5)
        vbox xysize(500,120):
            frame background Solid((255,255,255,150)) ysize 40 xfill True:
                if data[c].has_key('title_1'):
                    if len(data[c]['title_1']) > 40:
                        text "{color=#000}{size=-5}%s"%data[c]['title_1'] align(0.5,0.5)
                    else:
                        text "{color=#000}%s"%data[c]['title_1'] align(0.5,0.5)
                else:
                    text "{color=#000}No data" align(0.5,0.5)
            frame background Solid((0,0,0,150)) xfill True:
                vbox:
                    viewport id 'vp2':
                        child_size(480,10000)
                        xpos 10
                        draggable True
                        mousewheel True
                        if data[c].has_key('summary_1'):
                            text "{color=#fff}{size=-2}%s"%data[c]['summary_1'] align(0.5,0.5)
                        else:
                            text "{color=#fff}No data" align(0.5,0.5)
                    frame align(0.5,0.5) xsize 200:
                        if data[c].has_key('scene_1'):
                            textbutton ("Run") align(0.5,0.5) action Return(['run',data[c]['scene_1']])
                        else:
                            textbutton ("No data") align(0.5,0.5)

        vbox xysize(500,120):
            frame background Solid((255,255,255,150)) ysize 40 xfill True:
                if data[c].has_key('title_2'):
                    if len(data[c]['title_2']) > 40:
                        text "{color=#000}{size=-5}%s"%data[c]['title_2'] align(0.5,0.5)
                    else:
                        text "{color=#000}%s"%data[c]['title_2'] align(0.5,0.5)
                else:
                    text "{color=#000}No data" align(0.5,0.5)
            frame background Solid((0,0,0,150)) xfill True:
                vbox:
                    viewport id 'vp3':
                        child_size(480,10000)
                        xpos 10
                        draggable True
                        mousewheel True
                        if data[c].has_key('summary_2'):
                            text "{color=#fff}{size=-2}%s"%data[c]['summary_2'] align(0.5,0.5)
                        else:
                            text "{color=#fff}No data" align(0.5,0.5)
                    hbox align(0.5,0.5) spacing 20:
                        if data[c].has_key('scene_2'):
                            frame align(0.5,0.5) xsize 200:
                                textbutton ("Run intro") align(0.5,0.5) action Return(['run',data[c]['scene_2']])
                        else:
                            frame align(0.5,0.5) xsize 200:
                                textbutton ("No data") align(0.5,0.5)
                        if data[c].has_key('scene_3'):
                            frame align(0.5,0.5) xsize 200:
                                textbutton ("Run h-scene") align(0.5,0.5) action Return(['run',data[c]['scene_3']])
                        else:
                            frame align(0.5,0.5) xsize 200:
                                textbutton ("No data") align(0.5,0.5)

        if data[c]['type'] == 'kamihime_SR' or data[c]['type'] == 'kamihime_SSR' and ('Awakened' not in char_name and u'神化覚醒' not in char_name):
            vbox xysize(500,120):
                frame background Solid((255,255,255,150)) ysize 40 xfill True:
                    if data[c].has_key('title_4'):
                        if len(data[c]['title_4']) > 40:
                            text "{color=#000}{size=-5}%s"%data[c]['title_4'] align(0.5,0.5)
                        else:
                            text "{color=#000}%s"%data[c]['title_4'] align(0.5,0.5)
                    else:
                        text "{color=#000}No data" align(0.5,0.5)
                frame background Solid((0,0,0,150)) xfill True:
                    vbox:
                        viewport id 'vp4':
                            child_size(480,10000)
                            xpos 10
                            draggable True
                            mousewheel True
                            if data[c].has_key('summary_4'):
                                text "{color=#fff}{size=-2}%s"%data[c]['summary_4'] align(0.5,0.5)
                            else:
                                text "{color=#fff}No data" align(0.5,0.5)
                        hbox align(0.5,0.5) spacing 20:
                            if data[c].has_key('scene_4'):
                                frame align(0.5,0.5) xsize 200:
                                    textbutton ("Run intro") align(0.5,0.5) action Return(['run',data[c]['scene_4']])
                            else:
                                frame align(0.5,0.5) xsize 200:
                                    textbutton ("No data") align(0.5,0.5)
                            if data[c].has_key('scene_5'):
                                frame align(0.5,0.5) xsize 200:
                                    textbutton ("Run h-scene") align(0.5,0.5) action Return(['run',data[c]['scene_5']])
                            else:
                                frame align(0.5,0.5) xsize 200:
                                    textbutton ("No data") align(0.5,0.5) 

    if not renpy.music.is_playing():
        on "show" action mr.Play("bgm/%s"%bgm[persistent.bgm_index])


screen test:
    tag test
    add(Frame("backgrounds/%s"%(bg[bg_index])))
    hbox xfill True:
        imagebutton auto "gui/button/back-%s.png" align(0.0, 0.0) action Return(["back", "main_menu"])
        vbox xfill True spacing 10:
            hbox xalign 0.5 spacing 20:
                imagebutton auto "gui/button/story-%s.png" action Return(['info', 'Eleushkigar']) 
                imagebutton auto "gui/button/kamihime-%s.png"
                imagebutton auto "gui/button/eidolon-%s.png"
                imagebutton auto "gui/button/soul-%s.png"
            if True:
                hbox xalign 0.5 spacing 20:
                    imagebutton auto "gui/button/ssr-%s.png"
                    imagebutton auto "gui/button/sr-%s.png"
                    imagebutton auto "gui/button/rare-%s.png"
                    imagebutton auto "gui/button/other-%s.png"

    if not renpy.music.is_playing():
        on "show" action mr.Play()


screen custom_listener:
    key "K_t" action ToggleField(persistent, "text_enable", True, False)
    key "K_b" action [ToggleField(persistent, "bg_enable", True, False), Function(change_bg)]
    key "K_d" action [SetField(persistent, "bg_enable", False if persistent.text_enable else not persistent.bg_enable), 
                    SetField(persistent, "text_enable", False if persistent.text_enable != persistent.bg_enable else not persistent.text_enable),
                    Function(change_bg)]

label main_menu:
    return

            
label start:
    scene black
    show screen custom_listener
    python:
        change_bg()
        bg = os.listdir(os.path.join(config.gamedir, 'backgrounds'))
        bgm = os.listdir(os.path.join(config.gamedir, 'bgm'))
        persistent.bg_index = persistent.bg_index % len(bg)
        persistent.bgm_index = persistent.bgm_index % len(bgm)
        x_ratio = config.screen_width / 1280.0
        y_ratio = config.screen_height / 720.0
        
        mr = MusicRoom(fadeout=1.0, loop=True, single_track=True)
        for track in bgm:
            mr.add('bgm/%s' % track, always_unlocked=True)
        
        selected_category = ''
        selected_character = ''
        selected_platform = ''
        
        chars = dict(story=[],eidolon=[],soul=[],kamihime_R=[],kamihime_SR=[],kamihime_SSR=[],kamihime_unknown=[])
        nutaku_exist = False
        dmm_exist = False
        if os.path.exists(os.path.join(config.gamedir, 'nutaku')):
            nutaku_exist = True
            data_nutaku = dict_from_config_file(os.path.join(config.gamedir, 'nutaku/config.ini'))
            chars_nutaku = parse_character_info(data_nutaku, 'nutaku')
        if os.path.exists(os.path.join(config.gamedir, 'dmm')):
            dmm_exist = True
            data_dmm = dict_from_config_file(os.path.join(config.gamedir, 'dmm/config.ini'))
            chars_dmm = parse_character_info(data_dmm, 'dmm')
            

label index:
    $story = "index"
    if selected_category == '':
        hide screen index
        show screen main_menu
        show screen debugTools
    elif selected_category == 'story':
        show screen index
    else:
        show screen info
    window hide
    python:
        while True:
            result = ui.interact()
            if result[0] == 'run':
                story = result[1]
                renpy.hide_screen('index')
                renpy.hide_screen('info')
                ZoomConfig.reset()
                _window_show(trans=dissolve)
                renpy.jump(result[1])
            elif result[0] == 'back':
                if result[1] == 'index':
                    renpy.hide_screen("info")
                    renpy.show_screen("index")
                else:
                    renpy.hide_screen("index")
                    renpy.show_screen("main_menu")
            elif result[0] == 'index':
                selected_platform = result[1]
                if selected_platform == 'nutaku':
                    chars = chars_nutaku
                    data = data_nutaku
                else:
                    chars = chars_dmm
                    data = data_dmm                
                renpy.hide_screen('main_menu')
                renpy.show_screen('index')
            elif result[0] == 'info':
                selected_character = result[1]
                renpy.hide_screen('index')
                renpy.show_screen('info')
            elif result == 'exit':
                renpy.quit()
 
    return


screen debugTools:
    tag debugTools
    if config.developer:
        hbox:        
            xalign 0.0
            yalign 1.0
            button:
                text "{color=#fff}X"
                action ui.callsinnewcontext("_instant_exit")
            button:
                text "{color=#fff}R"
                action ui.callsinnewcontext("_save_reload_game")


label _instant_exit: 
    $renpy.quit()
    

init python:
    import os
    
    def to_safe_string(s):
        s = s.replace('[','')
        s = s.replace(']','')
        s = s.replace('(','')
        s = s.replace(')',' ')
        s = s.replace('  ',' ')
        return s

    def get_size(d):
        d = renpy.easy.displayable(d)
        w, h = renpy.render(d, 0, 0, 0, 0).get_size()
        w, h = int(round(w)), int(round(h))
        return w, h

    # ресайз картиники с сохранением соотношения сторон            
    def ProportionalScale(img, maxwidth, maxheight):
        currentwidth, currentheight = get_size(img)
        xscale = float(maxwidth) / float(currentwidth)
        yscale = float(maxheight) / float(currentheight)
        
        if xscale < yscale:
            minscale = xscale
        else:
            minscale = yscale
            
        newwidth = currentwidth * minscale
        newheight = currentheight * minscale
        
        return im.FactorScale(img,minscale,minscale)

    def scale(size, ratio, axis):
        if axis=='x':
            return int(size*ratio)
        else:
            return int(size*ratio)


screen lightbutton(img,return_value,align = (0.5,0.5)):
    imagebutton:
        align align
        idle (img)
        hover (im.MatrixColor(img,im.matrix.brightness(0.15)))
        action Return(return_value)


init python:
    def change_bg():
        if persistent.bg_enable:
            if style.say_window.background == None:
                style.say_window.background = Frame("gui/base_talk_window.png", xalign=0.5, yalign=1.0)
                style.say_dialogue.outlines = [ (absolute(0), "#FFF", absolute(0), absolute(0)) ]
                style.say_dialogue.color = "#000000"
                style.say_label.outlines = [ (absolute(0), "#000", absolute(0), absolute(0)) ]
                style.rebuild()
        else:
            if style.say_window.background != None:
                style.say_window.background = None
                style.say_dialogue.outlines = [ (absolute(2), "#000", absolute(1), absolute(1)) ]
                style.say_dialogue.color = "#FFFFFF"
                style.say_label.outlines = [ (absolute(2), "#000", absolute(1), absolute(1)) ]
                style.rebuild()

    def parse(string):
        try:
            value = int(string)
        except TypeError:
            value = string
        except AttributeError:
            value = string
        except ValueError:
            try:
                value = float(string)
            except ValueError:
                if string.lower() in ['true','yes','on']:
                    value = True
                elif string.lower() in ['false','no','off','none']:
                    value = False
                else:
                    value = string
        return value
 
    def dict_from_config_file(file, raw=False, vars=None): 
        result = dict()

        if file[-3:] == 'ini':
            """Convert an INI file to a dictionary""" #from cherrypy 
            import codecs
            inifile = ConfigParser() 
            inifile.readfp(codecs.open(file, 'r', encoding='utf-8'))
            # inifile.read(renpy.loader.transfn(file))
         
            # Load INI file into a dict 
            for section in inifile.sections(): 
                char_name = inifile.get(section, 'name', raw, vars)
                result[char_name] = dict() 
                result[char_name]['id'] = section
                for option in inifile.options(section): 
                    v = inifile.get(section, option, raw, vars) 
                    result[char_name][option] = parse(v)
        
        return result

    def parse_character_info(data, platform):
        from natsort import natsorted
        charlist = natsorted(data.keys())
        
        chars = dict(story=[],eidolon=[],soul=[],kamihime_R=[],kamihime_SR=[],kamihime_SSR=[])
        for c in charlist:
            if data[c]['type'] != 'story':
                portrait_full_path = os.path.join(config.gamedir, platform, 'portrait_full', '%s.png' % data[c]['name']).replace('\\', '/')
                if os.path.exists(portrait_full_path): 
                    data[c]['full_art'] = portrait_full_path
                else:
                    data[c]['full_art'] = 'blank.png'

                portrait_path = os.path.join(config.gamedir, platform, 'portrait', '%s.png' % data[c]['name']).replace('\\', '/')
                if os.path.exists(portrait_path):
                    data[c]['portrait'] = portrait_path
                else:
                    data[c]['portrait'] = None
                    
                keys_1_scene = {'title_1', 'title_2', 'scene_1', 'scene_2', 'scene_3'}
                keys_2_scene = {'title_1', 'title_2', 'title_4', 'scene_1', 'scene_2', 'scene_3', 'scene_4', 'scene_5'}
                if data[c]['type'] == 'kamihime_SR' or data[c]['type'] == 'kamihime_SSR':
                    if all(key in data[c] for key in keys_2_scene): # Full 5 scenarios
                        data[c]['color'] = (0,150,0,255)
                    else:
                        if "Awakened" in c or u'神化覚醒' in c: # Awakened case
                            if all(key in data[c] for key in keys_1_scene): # Full 3 scenarios
                                data[c]['color'] = (0,150,0,255)
                            elif all(key not in data[c] for key in keys_1_scene): # No scenario
                                data[c]['color'] = (150,0,0,255)
                            else: # Missing some scenarios
                                data[c]['color'] = (0,0,150,255)
                        elif all(key not in data[c] for key in keys_2_scene): # No scenario
                            data[c]['color'] = (150,0,0,255)
                        else: # Missing some scenarios
                            data[c]['color'] = (0,0,150,255)
                else: 
                    if all(key in data[c] for key in keys_1_scene): # Full 3 scenarios
                        data[c]['color'] = (0,150,0,255)
                    elif all(key not in data[c] for key in keys_1_scene): # No scenario
                        data[c]['color'] = (150,0,0,255)
                    else: # Missing some scenarios
                        data[c]['color'] = (0,0,150,255)

            chars[data[c]['type']].append(c)

        return chars
