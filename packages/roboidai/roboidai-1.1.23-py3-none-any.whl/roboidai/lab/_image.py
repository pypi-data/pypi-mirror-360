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
_O0O000O0O0OOO0OOO ={'en':{'capture_color':'Press SPACE key to collect color data or ESC key to quit.','capture_image':'Press SPACE key to save image or ESC key to quit.','record_image':'Press ESC key to quit.','saved':'saved'},'ko':{'capture_color':'스페이스 키를 누르면 색깔 데이터를 수집하고 ESC 키를 누르면 종료합니다.','capture_image':'스페이스 키를 누르면 영상 한 장을 저장하고 ESC 키를 누르면 종료합니다.','record_image':'ESC 키를 누르면 종료합니다.','saved':'저장됨'}}#line:23
_OOO0O00OOO00000O0 ={'hsv':cv2 .COLOR_BGR2HSV ,'ycrcb':cv2 .COLOR_BGR2YCrCb }#line:27
def collect_image (O00000O0000O0OO00 ,OOO0OO0OOOO0O00OO ,lang ='en'):#line:30
    print (translate ('lab._image.capture_image',lang ))#line:31
    O00OO0OO00OOO0O00 =0 #line:32
    while True :#line:33
        O0O00OOO0O0OO0000 ,O00O0O00O0O0000O0 =O00000O0000O0OO00 .read_until_key ()#line:34
        if O00O0O00O0O0000O0 =='esc':#line:35
            break #line:36
        elif O00O0O00O0O0000O0 ==' ':#line:37
            if (save_image (O0O00OOO0O0OO0000 ,OOO0OO0OOOO0O00OO )):#line:38
                O00OO0OO00OOO0O00 +=1 #line:39
                print (translate ('lab._image.saved',lang ),O00OO0OO00OOO0O00 )#line:40
def record_image (OO000OO00000OO000 ,O0O0OOOO0OOO00000 ,interval_msec =100 ,frames =20 ,countdown =3 ,lang ='en'):#line:42
    print (translate ('lab._image.record_image',lang ))#line:43
    if countdown >0 :#line:44
        OO000OO00000OO000 .count_down (countdown )#line:45
    OOO0OOOO0O0O000O0 =0 #line:46
    OOO0O00O0OOO0OOOO =timer ()#line:47
    while True :#line:48
        if OOO0OOOO0O0O000O0 >=frames :break #line:49
        OOO0O0OOO0OO00000 =OO000OO00000OO000 .read ()#line:50
        OO000OO00000OO000 .show (OOO0O0OOO0OO00000 )#line:51
        if timer ()>OOO0O00O0OOO0OOOO :#line:52
            if (save_image (OOO0O0OOO0OO00000 ,O0O0OOOO0OOO00000 )):#line:53
                OOO0OOOO0O0O000O0 +=1 #line:54
                print (translate ('lab._image.saved',lang ),OOO0OOOO0O0O000O0 )#line:55
            OOO0O00O0OOO0OOOO +=interval_msec /1000.0 #line:56
        if OO000OO00000OO000 .check_key ()=='esc':#line:57
            break #line:58
def save_image (OO000OOOOOOOO0000 ,O0000OO00OOOOO00O ,filename =None ):#line:60
    if OO000OOOOOOOO0000 is not None and O0000OO00OOOOO00O is not None :#line:61
        if not os .path .isdir (O0000OO00OOOOO00O ):#line:62
            os .makedirs (O0000OO00OOOOO00O )#line:63
        if filename is None :#line:64
            filename =datetime .now ().strftime ("%Y%m%d_%H%M%S_%f")+'.png'#line:65
        if cv2 .imwrite (os .path .join (O0000OO00OOOOO00O ,filename ),OO000OOOOOOOO0000 ):#line:66
            return True #line:67
        try :#line:68
            OO0O0000O0O000OO0 =os .path .splitext (filename )[1 ]#line:69
            O000O0OOO0O0OOO00 ,O000OOO00OO000OO0 =cv2 .imencode (OO0O0000O0O000OO0 ,OO000OOOOOOOO0000 )#line:70
            if O000O0OOO0O0OOO00 :#line:71
                with open (os .path .join (O0000OO00OOOOO00O ,filename ),mode ='w+b')as OOOO0OOO0OO0O0000 :#line:72
                    O000OOO00OO000OO0 .tofile (OOOO0OOO0OO0O0000 )#line:73
                return True #line:74
            else :#line:75
                return False #line:76
        except :#line:77
            return False #line:78
    return False #line:79
def collect_color (O00OO00O0O00O0OO0 ,OO000O00O0OO000OO ,color_space ='hsv',lang ='en'):#line:81
    OOOOO0OO0O00000O0 =None #line:82
    if isinstance (color_space ,(int ,float )):#line:83
        OOOOO0OO0O00000O0 =int (color_space )#line:84
    elif isinstance (color_space ,str ):#line:85
        color_space =color_space .lower ()#line:86
        if color_space in _OOO0O00OOO00000O0 :#line:87
            OOOOO0OO0O00000O0 =_OOO0O00OOO00000O0 [color_space ]#line:88
    O00O0O000O000O0O0 =[]#line:90
    OOOO0O0O0OOOOO000 =[]#line:91
    O0OOO00000OOO0OO0 =[]#line:92
    O0OOO0O0OO0O0O0OO =[]#line:93
    for OO0OO0OO00OOO0OO0 ,OOO00O0OOO00OOOOO in enumerate (OO000O00O0OO000OO ):#line:94
        print ('[{}] {}'.format (OOO00O0OOO00OOOOO ,_O0O000O0O0OOO0OOO [lang ]['capture_color']))#line:95
        OOO0OOO000000O0O0 ,OOO0O0OOO00O0OOO0 =O00OO00O0O00O0OO0 .read_until_key ()#line:96
        if OOO0O0OOO00O0OOO0 =='esc':#line:97
            O00OO00O0O00O0OO0 .hide ()#line:98
            return None ,None #line:99
        elif OOO0O0OOO00O0OOO0 ==' 'and OOO0OOO000000O0O0 is not None :#line:100
            O0OO0O000000O0OOO =OOO0OOO000000O0O0 if OOOOO0OO0O00000O0 is None else cv2 .cvtColor (OOO0OOO000000O0O0 ,OOOOO0OO0O00000O0 )#line:101
            O00O0O000O000O0O0 .append (O0OO0O000000O0OOO [:,:,0 ])#line:102
            OOOO0O0O0OOOOO000 .append (O0OO0O000000O0OOO [:,:,1 ])#line:103
            O0OOO00000OOO0OO0 .append (O0OO0O000000O0OOO [:,:,2 ])#line:104
            O0OOO0O0OO0O0O0OO .append ([OO0OO0OO00OOO0OO0 ]*(O0OO0O000000O0OOO .shape [0 ]*O0OO0O000000O0OOO .shape [1 ]))#line:105
    O00OO00O0O00O0OO0 .hide ()#line:106
    OOO00000O0O000O00 =np .concatenate (O00O0O000O000O0O0 ,axis =None ).reshape (-1 ,1 )#line:108
    OOO0O0O0000O000OO =np .concatenate (OOOO0O0O0OOOOO000 ,axis =None ).reshape (-1 ,1 )#line:109
    OO0O0OO000O0O000O =np .concatenate (O0OOO00000OOO0OO0 ,axis =None ).reshape (-1 ,1 )#line:110
    O000O0000O0O00O0O =np .concatenate (O0OOO0O0OO0O0O0OO ,axis =None )#line:111
    O00O0000OO00OO00O =np .hstack ((OOO00000O0O000O00 ,OOO0O0O0000O000OO ,OO0O0OO000O0O000O ))#line:112
    return O00O0000OO00OO00O ,O000O0000O0O00O0O #line:114
def capture_color (O0OOOOO00O0O0OO0O ,color_space ='hsv',lang ='en'):#line:116
    O0O0O0O0OO00O0000 =None #line:117
    if isinstance (color_space ,(int ,float )):#line:118
        O0O0O0O0OO00O0000 =int (color_space )#line:119
    elif isinstance (color_space ,str ):#line:120
        color_space =color_space .lower ()#line:121
        if color_space in _OOO0O00OOO00000O0 :#line:122
            O0O0O0O0OO00O0000 =_OOO0O00OOO00000O0 [color_space ]#line:123
    OO00O0O00OO0OO000 =None #line:125
    print (_O0O000O0O0OOO0OOO [lang ]['capture_color'])#line:126
    OO000O00OO00O0OO0 ,O0OOO0OO00OO00OOO =O0OOOOO00O0O0OO0O .read_until_key ()#line:127
    if O0OOO0OO00OO00OOO =='esc':#line:128
        O0OOOOO00O0O0OO0O .hide ()#line:129
        return None #line:130
    elif O0OOO0OO00OO00OOO ==' 'and OO000O00OO00O0OO0 is not None :#line:131
        OO00O0OOO0O0O0O00 =OO000O00OO00O0OO0 if O0O0O0O0OO00O0000 is None else cv2 .cvtColor (OO000O00OO00O0OO0 ,O0O0O0O0OO00O0000 )#line:132
        O00OO0OOOOOO0O00O =OO00O0OOO0O0O0O00 [:,:,0 ].reshape (-1 ,1 )#line:133
        O0OO00O0000OO0O00 =OO00O0OOO0O0O0O00 [:,:,1 ].reshape (-1 ,1 )#line:134
        O00OO00OOOO0OO0OO =OO00O0OOO0O0O0O00 [:,:,2 ].reshape (-1 ,1 )#line:135
        OO00O0O00OO0OO000 =np .hstack ((O00OO0OOOOOO0O00O ,O0OO00O0000OO0O00 ,O00OO00OOOO0OO0OO ))#line:136
    O0OOOOO00O0O0OO0O .hide ()#line:137
    return OO00O0O00OO0OO000 #line:138
