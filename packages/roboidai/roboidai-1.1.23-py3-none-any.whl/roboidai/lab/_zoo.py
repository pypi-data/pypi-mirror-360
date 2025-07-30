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

_OOOOOO0OOO0OOO000 ={'en':['bird','dog','elephant','zebra'],'ko':['새','개','코끼리','얼룩말']}#line:6
_OO0OO0O0O000O0OO0 ={'en':{'init':'Place your robot on the starting position and align the direction.','show_animal':'Show the animal on the camera.','guess':'It looks like a(n) {0}. Let\'s move to the {0}\'s house.','replay':'Replay? [y/n]','wing':'Does it have wings?','nose':'Does it have a very long nose?','stripe':'Does it have stripes on the body?','bird':'bird','dog':'dog','elephant':'elephant','zebra':'zebra'},'ko':{'init':'로봇을 출발지에 방향을 맞추어 올려 놓아 주세요.','show_animal':'카메라에 동물을 보여 주세요.','guess':'{0}인 것 같네요. {0} 집으로 이동합니다.','replay':'다시 시작할까요? [y/n]','wing':'날개가 있습니까?','nose':'코가 아주 깁니까?','stripe':'몸에 줄무늬가 있습니까?','bird':'새','dog':'개','elephant':'코끼리','zebra':'얼룩말'}}#line:34
def move_zoo (O0OOO0OOOO0000OO0 ,O00OOO0OO0OOO0OOO ,lang ='en'):#line:37
    if O00OOO0OO0OOO0OOO ==_OOOOOO0OOO0OOO000 [lang ][0 ]:#line:38
        O0OOO0OOOO0000OO0 .board_forward ()#line:39
        O0OOO0OOOO0000OO0 .board_left ()#line:40
        O0OOO0OOOO0000OO0 .board_forward ()#line:41
    elif O00OOO0OO0OOO0OOO ==_OOOOOO0OOO0OOO000 [lang ][1 ]:#line:42
        O0OOO0OOOO0000OO0 .board_forward ()#line:43
        O0OOO0OOOO0000OO0 .board_right ()#line:44
        O0OOO0OOOO0000OO0 .board_forward ()#line:45
    elif O00OOO0OO0OOO0OOO ==_OOOOOO0OOO0OOO000 [lang ][2 ]:#line:46
        O0OOO0OOOO0000OO0 .board_forward ()#line:47
        O0OOO0OOOO0000OO0 .board_forward ()#line:48
        O0OOO0OOOO0000OO0 .board_left ()#line:49
        O0OOO0OOOO0000OO0 .board_forward ()#line:50
    elif O00OOO0OO0OOO0OOO ==_OOOOOO0OOO0OOO000 [lang ][3 ]:#line:51
        O0OOO0OOOO0000OO0 .board_forward ()#line:52
        O0OOO0OOOO0000OO0 .board_forward ()#line:53
        O0OOO0OOOO0000OO0 .board_right ()#line:54
        O0OOO0OOOO0000OO0 .board_forward ()#line:55
def play_zoo_cam (O0OO0O000O0O0O0O0 ,OO0O00O000O0OOOOO ,model_folder =None ,lang ='en'):#line:57
    import roboid #line:58
    import roboidai as ai #line:59
    OO000OO0O0OOOO00O =ai .ObjectDetector (lang =lang )#line:61
    OO000OO0O0OOOO00O .download_model (model_folder )#line:62
    OO000OO0O0OOOO00O .load_model (model_folder )#line:63
    while True :#line:65
        print ()#line:66
        print (_OO0OO0O0O000O0OO0 [lang ]['init'])#line:67
        print (_OO0OO0O0O000O0OO0 [lang ]['show_animal'])#line:68
        while True :#line:69
            OOOOO00OO000000OO =OO0O00O000O0OOOOO .read ()#line:70
            if OO000OO0O0OOOO00O .detect (OOOOO00OO000000OO ):#line:71
                O0OO00O00O0O0000O =OO000OO0O0OOOO00O .get_label ()#line:72
                if O0OO00O00O0O0000O in _OOOOOO0OOO0OOO000 [lang ]:#line:73
                    OO0O00O000O0OOOOO .hide ()#line:74
                    print (_OO0OO0O0O000O0OO0 [lang ]['guess'].format (O0OO00O00O0O0000O ))#line:75
                    move_zoo (O0OO0O000O0O0O0O0 ,O0OO00O00O0O0000O ,lang )#line:76
                    roboid .wait (200 )#line:77
                    break #line:78
            OO0O00O000O0OOOOO .show (OOOOO00OO000000OO )#line:79
            if OO0O00O000O0OOOOO .check_key ()=='esc':#line:80
                break #line:81
        print (_OO0OO0O0O000O0OO0 [lang ]['replay'])#line:82
        if input ()!='y':#line:83
            break #line:84
    O0OO0O000O0O0O0O0 .stop ()#line:85
    roboid .wait (100 )#line:86
def play_zoo_tree (OOOOOO0000O0O0O00 ,lang ='en'):#line:88
    import roboid #line:89
    from ._tree import Node #line:90
    O0O0000000OO0O0O0 =Node (_OO0OO0O0O000O0OO0 [lang ]['wing'])#line:92
    O0O0000000OO0O0O0 .add_left (_OO0OO0O0O000O0OO0 [lang ]['bird'])#line:93
    O0O0OOOO00OO0000O =O0O0000000OO0O0O0 .add_right (_OO0OO0O0O000O0OO0 [lang ]['nose'])#line:94
    O0O0OOOO00OO0000O .add_left (_OO0OO0O0O000O0OO0 [lang ]['elephant'])#line:95
    O0O0OOOO00OO0000O =O0O0OOOO00OO0000O .add_right (_OO0OO0O0O000O0OO0 [lang ]['stripe'])#line:96
    O0O0OOOO00OO0000O .add_left (_OO0OO0O0O000O0OO0 [lang ]['zebra'])#line:97
    O0O0OOOO00OO0000O .add_right (_OO0OO0O0O000O0OO0 [lang ]['dog'])#line:98
    while True :#line:100
        print ()#line:101
        print (_OO0OO0O0O000O0OO0 [lang ]['init'])#line:102
        O0O0OOOO00OO0000O =O0O0000000OO0O0O0 #line:103
        while True :#line:104
            if O0O0OOOO00OO0000O .is_terminal ():#line:105
                OOO000O0OOO000000 =O0O0OOOO00OO0000O .get_key ()#line:106
                print (_OO0OO0O0O000O0OO0 [lang ]['guess'].format (OOO000O0OOO000000 ))#line:107
                break #line:108
            else :#line:109
                print (O0O0OOOO00OO0000O .get_key ()+'[y/n]')#line:110
                if input ()=='y':#line:111
                    O0O0OOOO00OO0000O =O0O0OOOO00OO0000O .get_left ()#line:112
                else :#line:113
                    O0O0OOOO00OO0000O =O0O0OOOO00OO0000O .get_right ()#line:114
        move_zoo (OOOOOO0000O0O0O00 ,OOO000O0OOO000000 ,lang )#line:115
        print (_OO0OO0O0O000O0OO0 [lang ]['replay'])#line:116
        if input ()=='y':#line:117
            O0O0OOOO00OO0000O =O0O0000000OO0O0O0 #line:118
        else :#line:119
            break #line:120
    OOOOOO0000O0O0O00 .stop ()#line:121
    roboid .wait (100 )#line:122
