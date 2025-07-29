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

import cv2 #line:2
import numpy as np #line:3
import os #line:4
from datetime import datetime #line:5
from timeit import default_timer as timer #line:6
from roboidai ._lang import translate #line:7
_O0OO0OO00O0O0O0OO ={'en':{'capture_color':'Press SPACE key to collect color data or ESC key to quit.','capture_image':'Press SPACE key to save image or ESC key to quit.','record_image':'Press ESC key to quit.','saved':'saved'},'ko':{'capture_color':'스페이스 키를 누르면 색깔 데이터를 수집하고 ESC 키를 누르면 종료합니다.','capture_image':'스페이스 키를 누르면 영상 한 장을 저장하고 ESC 키를 누르면 종료합니다.','record_image':'ESC 키를 누르면 종료합니다.','saved':'저장됨'}}#line:23
_OOOO0000OO00O000O ={'hsv':cv2 .COLOR_BGR2HSV ,'ycrcb':cv2 .COLOR_BGR2YCrCb }#line:27
def collect_image (O00000O0O00O00OO0 ,O00OOO0O0OO00O0O0 ,lang ='en'):#line:30
    print (translate ('lab._image.capture_image',lang ))#line:31
    OOO0OO0O0O00O0O0O =0 #line:32
    while True :#line:33
        O0OOOOOO0O00OOOOO ,O0OOOOOOO0O00000O =O00000O0O00O00OO0 .read_until_key ()#line:34
        if O0OOOOOOO0O00000O =='esc':#line:35
            break #line:36
        elif O0OOOOOOO0O00000O ==' ':#line:37
            if (save_image (O0OOOOOO0O00OOOOO ,O00OOO0O0OO00O0O0 )):#line:38
                OOO0OO0O0O00O0O0O +=1 #line:39
                print (translate ('lab._image.saved',lang ),OOO0OO0O0O00O0O0O )#line:40
def record_image (OO000O00OO0O0000O ,O000O0000O0OO0O00 ,interval_msec =100 ,frames =20 ,countdown =3 ,lang ='en'):#line:42
    print (translate ('lab._image.record_image',lang ))#line:43
    if countdown >0 :#line:44
        OO000O00OO0O0000O .count_down (countdown )#line:45
    O00O0000OOOO0OO00 =0 #line:46
    OOO0OO0O0O0O0OO00 =timer ()#line:47
    while True :#line:48
        if O00O0000OOOO0OO00 >=frames :break #line:49
        OO00OO00O0OOO00O0 =OO000O00OO0O0000O .read ()#line:50
        OO000O00OO0O0000O .show (OO00OO00O0OOO00O0 )#line:51
        if timer ()>OOO0OO0O0O0O0OO00 :#line:52
            if (save_image (OO00OO00O0OOO00O0 ,O000O0000O0OO0O00 )):#line:53
                O00O0000OOOO0OO00 +=1 #line:54
                print (translate ('lab._image.saved',lang ),O00O0000OOOO0OO00 )#line:55
            OOO0OO0O0O0O0OO00 +=interval_msec /1000.0 #line:56
        if OO000O00OO0O0000O .check_key ()=='esc':#line:57
            break #line:58
def save_image (OO000000O00OOOOOO ,O0O0O00OO00OO0OOO ,filename =None ):#line:60
    if OO000000O00OOOOOO is not None and O0O0O00OO00OO0OOO is not None :#line:61
        if not os .path .isdir (O0O0O00OO00OO0OOO ):#line:62
            os .makedirs (O0O0O00OO00OO0OOO )#line:63
        if filename is None :#line:64
            filename =datetime .now ().strftime ("%Y%m%d_%H%M%S_%f")+'.png'#line:65
        if cv2 .imwrite (os .path .join (O0O0O00OO00OO0OOO ,filename ),OO000000O00OOOOOO ):#line:66
            return True #line:67
        try :#line:68
            O00OOOOOO0O00O0OO =os .path .splitext (filename )[1 ]#line:69
            O00OOOOOO00000O0O ,O00OOOOOO00OOOO0O =cv2 .imencode (O00OOOOOO0O00O0OO ,OO000000O00OOOOOO )#line:70
            if O00OOOOOO00000O0O :#line:71
                with open (os .path .join (O0O0O00OO00OO0OOO ,filename ),mode ='w+b')as O00OO00OOOO0OO0O0 :#line:72
                    O00OOOOOO00OOOO0O .tofile (O00OO00OOOO0OO0O0 )#line:73
                return True #line:74
            else :#line:75
                return False #line:76
        except :#line:77
            return False #line:78
    return False #line:79
def collect_color (O00O0OOOO000O00OO ,O000000OOOO000O00 ,color_space ='hsv',lang ='en'):#line:81
    O000O0O0O0OOOOOOO =None #line:82
    if isinstance (color_space ,(int ,float )):#line:83
        O000O0O0O0OOOOOOO =int (color_space )#line:84
    elif isinstance (color_space ,str ):#line:85
        color_space =color_space .lower ()#line:86
        if color_space in _OOOO0000OO00O000O :#line:87
            O000O0O0O0OOOOOOO =_OOOO0000OO00O000O [color_space ]#line:88
    OOO0OO00O00000000 =[]#line:90
    O0OO0000000O00O0O =[]#line:91
    O0OO0O00OO0O000O0 =[]#line:92
    O00O000O0000OOOO0 =[]#line:93
    for O000000OOOO0OOOOO ,O00O0OO000OO0O00O in enumerate (O000000OOOO000O00 ):#line:94
        print ('[{}] {}'.format (O00O0OO000OO0O00O ,_O0OO0OO00O0O0O0OO [lang ]['capture_color']))#line:95
        OOOO00O0OO00O00O0 ,OO0OOOOO0O0O0OOOO =O00O0OOOO000O00OO .read_until_key ()#line:96
        if OO0OOOOO0O0O0OOOO =='esc':#line:97
            O00O0OOOO000O00OO .hide ()#line:98
            return None ,None #line:99
        elif OO0OOOOO0O0O0OOOO ==' 'and OOOO00O0OO00O00O0 is not None :#line:100
            O00O0OOO00OOO0O0O =OOOO00O0OO00O00O0 if O000O0O0O0OOOOOOO is None else cv2 .cvtColor (OOOO00O0OO00O00O0 ,O000O0O0O0OOOOOOO )#line:101
            OOO0OO00O00000000 .append (O00O0OOO00OOO0O0O [:,:,0 ])#line:102
            O0OO0000000O00O0O .append (O00O0OOO00OOO0O0O [:,:,1 ])#line:103
            O0OO0O00OO0O000O0 .append (O00O0OOO00OOO0O0O [:,:,2 ])#line:104
            O00O000O0000OOOO0 .append ([O000000OOOO0OOOOO ]*(O00O0OOO00OOO0O0O .shape [0 ]*O00O0OOO00OOO0O0O .shape [1 ]))#line:105
    O00O0OOOO000O00OO .hide ()#line:106
    OOO0O00000O0OO0OO =np .concatenate (OOO0OO00O00000000 ,axis =None ).reshape (-1 ,1 )#line:108
    O0O0OO0000O00OO00 =np .concatenate (O0OO0000000O00O0O ,axis =None ).reshape (-1 ,1 )#line:109
    O0O00OOOO00OO00OO =np .concatenate (O0OO0O00OO0O000O0 ,axis =None ).reshape (-1 ,1 )#line:110
    O0OO000OO0000OOOO =np .concatenate (O00O000O0000OOOO0 ,axis =None )#line:111
    OO000000O000O0O00 =np .hstack ((OOO0O00000O0OO0OO ,O0O0OO0000O00OO00 ,O0O00OOOO00OO00OO ))#line:112
    return OO000000O000O0O00 ,O0OO000OO0000OOOO #line:114
def capture_color (O00O0O0OOOOO00000 ,color_space ='hsv',lang ='en'):#line:116
    OOO000O0O0O0O0O00 =None #line:117
    if isinstance (color_space ,(int ,float )):#line:118
        OOO000O0O0O0O0O00 =int (color_space )#line:119
    elif isinstance (color_space ,str ):#line:120
        color_space =color_space .lower ()#line:121
        if color_space in _OOOO0000OO00O000O :#line:122
            OOO000O0O0O0O0O00 =_OOOO0000OO00O000O [color_space ]#line:123
    OOOO00000OOO00O0O =None #line:125
    print (_O0OO0OO00O0O0O0OO [lang ]['capture_color'])#line:126
    OOO0OO00O000OO000 ,OO00O0OO0O00OO000 =O00O0O0OOOOO00000 .read_until_key ()#line:127
    if OO00O0OO0O00OO000 =='esc':#line:128
        O00O0O0OOOOO00000 .hide ()#line:129
        return None #line:130
    elif OO00O0OO0O00OO000 ==' 'and OOO0OO00O000OO000 is not None :#line:131
        OO00OOO0O0O0000OO =OOO0OO00O000OO000 if OOO000O0O0O0O0O00 is None else cv2 .cvtColor (OOO0OO00O000OO000 ,OOO000O0O0O0O0O00 )#line:132
        O0OO000O0OO0O0O0O =OO00OOO0O0O0000OO [:,:,0 ].reshape (-1 ,1 )#line:133
        OO00OOO00O0OOO0OO =OO00OOO0O0O0000OO [:,:,1 ].reshape (-1 ,1 )#line:134
        O000OO000OO0O0000 =OO00OOO0O0O0000OO [:,:,2 ].reshape (-1 ,1 )#line:135
        OOOO00000OOO00O0O =np .hstack ((O0OO000O0OO0O0O0O ,OO00OOO00O0OOO0OO ,O000OO000OO0O0000 ))#line:136
    O00O0O0OOOOO00000 .hide ()#line:137
    return OOOO00000OOO00O0O #line:138
