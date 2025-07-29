# Part of the ROBOID project - http://hamster.school
# Copyright (C) 2016 Kwang-Hyun Park (akaii@kw.ac.kr)
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General
# Public License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

_O00OO0O0O0OOO0000 ={'en':['bird','dog','elephant','zebra'],'ko':['새','개','코끼리','얼룩말']}#line:5
_O0O0OOOO00O00O00O ={'en':{'init':'Place your robot on the starting position and align the direction.','show_animal':'Show the animal on the camera.','guess':'It looks like a(n) {0}. Let\'s move to the {0}\'s house.','replay':'Replay? [y/n]','wing':'Does it have wings?','nose':'Does it have a very long nose?','stripe':'Does it have stripes on the body?','bird':'bird','dog':'dog','elephant':'elephant','zebra':'zebra'},'ko':{'init':'로봇을 출발지에 방향을 맞추어 올려 놓아 주세요.','show_animal':'카메라에 동물을 보여 주세요.','guess':'{0}인 것 같네요. {0} 집으로 이동합니다.','replay':'다시 시작할까요? [y/n]','wing':'날개가 있습니까?','nose':'코가 아주 깁니까?','stripe':'몸에 줄무늬가 있습니까?','bird':'새','dog':'개','elephant':'코끼리','zebra':'얼룩말'}}#line:33
def move_zoo (O0O0OOOO0O00OO000 ,OO0OO0OO0O00OO0OO ,lang ='en'):#line:36
    if OO0OO0OO0O00OO0OO ==_O00OO0O0O0OOO0000 [lang ][0 ]:#line:37
        O0O0OOOO0O00OO000 .board_forward ()#line:38
        O0O0OOOO0O00OO000 .board_left ()#line:39
        O0O0OOOO0O00OO000 .board_forward ()#line:40
    elif OO0OO0OO0O00OO0OO ==_O00OO0O0O0OOO0000 [lang ][1 ]:#line:41
        O0O0OOOO0O00OO000 .board_forward ()#line:42
        O0O0OOOO0O00OO000 .board_right ()#line:43
        O0O0OOOO0O00OO000 .board_forward ()#line:44
    elif OO0OO0OO0O00OO0OO ==_O00OO0O0O0OOO0000 [lang ][2 ]:#line:45
        O0O0OOOO0O00OO000 .board_forward ()#line:46
        O0O0OOOO0O00OO000 .board_forward ()#line:47
        O0O0OOOO0O00OO000 .board_left ()#line:48
        O0O0OOOO0O00OO000 .board_forward ()#line:49
    elif OO0OO0OO0O00OO0OO ==_O00OO0O0O0OOO0000 [lang ][3 ]:#line:50
        O0O0OOOO0O00OO000 .board_forward ()#line:51
        O0O0OOOO0O00OO000 .board_forward ()#line:52
        O0O0OOOO0O00OO000 .board_right ()#line:53
        O0O0OOOO0O00OO000 .board_forward ()#line:54
def play_zoo_cam (O0OO00000O000000O ,O00OO00OOOO00O00O ,model_folder =None ,lang ='en'):#line:56
    import roboid #line:57
    import roboidai as ai #line:58
    OO0000000000OO0OO =ai .ObjectDetector (lang =lang )#line:60
    OO0000000000OO0OO .download_model (model_folder )#line:61
    OO0000000000OO0OO .load_model (model_folder )#line:62
    while True :#line:64
        print ()#line:65
        print (_O0O0OOOO00O00O00O [lang ]['init'])#line:66
        print (_O0O0OOOO00O00O00O [lang ]['show_animal'])#line:67
        while True :#line:68
            O0O00O0OO0OO00O0O =O00OO00OOOO00O00O .read ()#line:69
            if OO0000000000OO0OO .detect (O0O00O0OO0OO00O0O ):#line:70
                OO00O000OO0OOOOOO =OO0000000000OO0OO .get_label ()#line:71
                if OO00O000OO0OOOOOO in _O00OO0O0O0OOO0000 [lang ]:#line:72
                    O00OO00OOOO00O00O .hide ()#line:73
                    print (_O0O0OOOO00O00O00O [lang ]['guess'].format (OO00O000OO0OOOOOO ))#line:74
                    move_zoo (O0OO00000O000000O ,OO00O000OO0OOOOOO ,lang )#line:75
                    roboid .wait (200 )#line:76
                    break #line:77
            O00OO00OOOO00O00O .show (O0O00O0OO0OO00O0O )#line:78
            if O00OO00OOOO00O00O .check_key ()=='esc':#line:79
                break #line:80
        print (_O0O0OOOO00O00O00O [lang ]['replay'])#line:81
        if input ()!='y':#line:82
            break #line:83
    O0OO00000O000000O .stop ()#line:84
    roboid .wait (100 )#line:85
def play_zoo_tree (O0OO0O0OO000O0000 ,lang ='en'):#line:87
    import roboid #line:88
    from ._tree import Node #line:89
    O0O0OO0000OOOOOO0 =Node (_O0O0OOOO00O00O00O [lang ]['wing'])#line:91
    O0O0OO0000OOOOOO0 .add_left (_O0O0OOOO00O00O00O [lang ]['bird'])#line:92
    O000OOOO00OO00000 =O0O0OO0000OOOOOO0 .add_right (_O0O0OOOO00O00O00O [lang ]['nose'])#line:93
    O000OOOO00OO00000 .add_left (_O0O0OOOO00O00O00O [lang ]['elephant'])#line:94
    O000OOOO00OO00000 =O000OOOO00OO00000 .add_right (_O0O0OOOO00O00O00O [lang ]['stripe'])#line:95
    O000OOOO00OO00000 .add_left (_O0O0OOOO00O00O00O [lang ]['zebra'])#line:96
    O000OOOO00OO00000 .add_right (_O0O0OOOO00O00O00O [lang ]['dog'])#line:97
    while True :#line:99
        print ()#line:100
        print (_O0O0OOOO00O00O00O [lang ]['init'])#line:101
        O000OOOO00OO00000 =O0O0OO0000OOOOOO0 #line:102
        while True :#line:103
            if O000OOOO00OO00000 .is_terminal ():#line:104
                O00000O00OO0000O0 =O000OOOO00OO00000 .get_key ()#line:105
                print (_O0O0OOOO00O00O00O [lang ]['guess'].format (O00000O00OO0000O0 ))#line:106
                break #line:107
            else :#line:108
                print (O000OOOO00OO00000 .get_key ()+'[y/n]')#line:109
                if input ()=='y':#line:110
                    O000OOOO00OO00000 =O000OOOO00OO00000 .get_left ()#line:111
                else :#line:112
                    O000OOOO00OO00000 =O000OOOO00OO00000 .get_right ()#line:113
        move_zoo (O0OO0O0OO000O0000 ,O00000O00OO0000O0 ,lang )#line:114
        print (_O0O0OOOO00O00O00O [lang ]['replay'])#line:115
        if input ()=='y':#line:116
            O000OOOO00OO00000 =O0O0OO0000OOOOOO0 #line:117
        else :#line:118
            break #line:119
    O0OO0O0OO000O0000 .stop ()#line:120
    roboid .wait (100 )#line:121
