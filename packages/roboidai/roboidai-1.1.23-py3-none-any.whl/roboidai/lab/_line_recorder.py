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

from roboid import *#line:2
from roboidai import KeyEvent #line:3
import os #line:4
import pandas as pd #line:5
_O0O0OO0000OOO0OO0 ={'en':{'usage':'Press space key to move.\nPress s key to save.\nPress ESC key to quit.\n','saved':'Saved to {}'},'ko':{'usage':'스페이스 키를 누르면 이동합니다.\ns키를 누르면 저장합니다.\nESC 키를 누르면 종료합니다.\n','saved':'{}에 저장되었습니다.'}}#line:17
class _OOOOO0OOO00OO0O0O :#line:20
    _STATE_IDLE =0 #line:21
    _STATE_MOVE =1 #line:22
    def _usage (OOO0OO00O0000O0OO ,lang ='en'):#line:24
        print (_O0O0OO0000OOO0OO0 [lang ]['usage'])#line:25
    def start (O00O0OO0OO00O0OOO ,OOOOOO00O000OO0OO ,lang ='en'):#line:27
        O00O0OO0OO00O0OOO ._usage (lang )#line:28
        KeyEvent .start ()#line:29
class _O0O0O000OOOOOOO00 (_OOOOO0OOO00OO0O0O ):#line:32
    def _create_robot (OOO00OO000OOO000O ):#line:33
        return None #line:34
    def _save (O00O0000000O0O000 ,OO0OO0O0OO0O0O000 ,O0OOO000000000OO0 ):#line:36
        if isinstance (O0OOO000000000OO0 ,str ):#line:37
            OO000OO000O00O0OO =os .path .dirname (O0OOO000000000OO0 )#line:38
            if not os .path .isdir (OO000OO000O00O0OO ):#line:39
                os .makedirs (OO000OO000O00O0OO )#line:40
        OO0OO0O0OO0O0O000 .to_csv (O0OOO000000000OO0 ,index =False )#line:41
    def start (OO00OO0OO0OOO00O0 ,O0O0OO0OOOO0O0O0O ,lang ='en'):#line:43
        super (_O0O0O000OOOOOOO00 ,OO00OO0OO0OOO00O0 ).start (O0O0OO0OOOO0O0O0O ,lang )#line:44
        O0OOOO0OOOOO00OOO =OO00OO0OO0OOO00O0 ._create_robot ()#line:46
        if O0OOOO0OOOOO00OOO is None :#line:47
            KeyEvent .stop ()#line:48
            return #line:49
        OO00000O0OOOOOO00 =[]#line:51
        O0OOO00OO0O00000O =[]#line:52
        O0OO0OO0OOOOOOO0O =[]#line:53
        O00O0OOOOO0OO00OO =_OOOOO0OOO00OO0O0O ._STATE_IDLE #line:54
        O0OO000OOOOOO00OO =0 #line:55
        O0000OO00OOO0O00O =False #line:56
        while True :#line:58
            O0OO0O00OO0OOOOOO =KeyEvent .get_released_key ()#line:59
            if O00O0OOOOO0OO00OO ==_OOOOO0OOO00OO0O0O ._STATE_IDLE :#line:60
                if O0OO0O00OO0OOOOOO ==KeyEvent .SPACE :#line:61
                    O00O0OOOOO0OO00OO =_OOOOO0OOO00OO0O0O ._STATE_MOVE #line:62
                    OO00O00O0000OO0OO =[]#line:63
                    OOOOOO0OOOO00O00O =[]#line:64
                    OOO0O0O0O0OO0OOOO =[]#line:65
            elif O00O0OOOOO0OO00OO ==_OOOOO0OOO00OO0O0O ._STATE_MOVE :#line:66
                OOOO00OO0OOO000OO =(OO0O0O00OOO00O000 -50 )*0.5 #line:67
                O000OO00O00OOOOO0 =30 +OOOO00OO0OOO000OO #line:68
                OOO000O00OOO0O0OO =30 -OOOO00OO0OOO000OO #line:69
                O0OOOO0OOOOO00OOO .wheels (O000OO00O00OOOOO0 ,OOO000O00OOO0O0OO )#line:70
                if O0000OO00OOO0O00O :#line:71
                    OO00O00O0000OO0OO .append (O0OOOO0OOOOO00OOO .left_floor ())#line:72
                    OOOOOO0OOOO00O00O .append (O000OO00O00OOOOO0 )#line:73
                    OOO0O0O0O0OO0OOOO .append (OOO000O00OOO0O0OO )#line:74
                if OO0O0O00OOO00O000 <30 and OOO0000O000O0OOOO <30 :#line:76
                    O0OO000OOOOOO00OO +=1 #line:77
                    O0000OO00OOO0O00O =False #line:78
                    if O0OO000OOOOOO00OO >3 :#line:79
                        O0OOOO0OOOOO00OOO .stop ()#line:80
                        O00O0OOOOO0OO00OO =_OOOOO0OOO00OO0O0O ._STATE_IDLE #line:81
                        O0OO000OOOOOO00OO =0 #line:82
                        OO00000O0OOOOOO00 .extend (OO00O00O0000OO0OO [20 :-20 ])#line:83
                        O0OOO00OO0O00000O .extend (OOOOOO0OOOO00O00O [20 :-20 ])#line:84
                        O0OO0OO0OOOOOOO0O .extend (OOO0O0O0O0OO0OOOO [20 :-20 ])#line:85
                else :#line:86
                    O0OO000OOOOOO00OO =0 #line:87
                    O0000OO00OOO0O00O =True #line:88
            OO0O0O00OOO00O000 =O0OOOO0OOOOO00OOO .left_floor ()#line:90
            OOO0000O000O0OOOO =O0OOOO0OOOOO00OOO .right_floor ()#line:91
            if O0OO0O00OO0OOOOOO =='s':#line:92
                OOOO0O00O0O000O00 =pd .DataFrame ({'left_floor':OO00000O0OOOOOO00 ,'left_wheel':O0OOO00OO0O00000O ,'right_wheel':O0OO0OO0OOOOOOO0O })#line:95
                OO00OO0OO0OOO00O0 ._save (OOOO0O00O0O000O00 ,O0O0OO0OOOO0O0O0O )#line:96
                print (_O0O0OO0000OOO0OO0 [lang ]['saved'].format (O0O0OO0OOOO0O0O0O ))#line:97
            elif O0OO0O00OO0OOOOOO ==KeyEvent .ESC :#line:98
                break #line:99
            wait (20 )#line:101
        KeyEvent .stop ()#line:103
        O0OOOO0OOOOO00OOO .dispose ()#line:104
class _O0OO0O0O0OO0O0OO0 (_O0O0O000OOOOOOO00 ):#line:107
    def _create_robot (O0O000OOOOOOO00OO ):#line:108
        return Hamster ()#line:109
class _OOO0OOOOO0OOOOO00 (_O0O0O000OOOOOOO00 ):#line:112
    def _create_robot (O0O0O00O0O0O000OO ):#line:113
        return HamsterS ()#line:114
class _OOO00OOO0000000OO (_O0O0O000OOOOOOO00 ):#line:117
    def __init__ (OO00OO0O0000OO0O0 ,O00O0OO000OO000O0 ):#line:118
        OO00OO0O0000OO0O0 ._robot =O00O0OO000OO000O0 #line:119
    def _create_robot (O0OO0O00000OO00O0 ):#line:121
        return O0OO0O00000OO00O0 ._robot #line:122
def record_hamster (O0OOOOOO00OOOO0OO ,lang ='en'):#line:125
    _O0OO0O0O0OO0O0OO0 ().start (O0OOOOOO00OOOO0OO ,lang )#line:126
def record_hamster_s (OO00OO000OOOO0OOO ,lang ='en'):#line:128
    _OOO0OOOOO0OOOOO00 ().start (OO00OO000OOOO0OOO ,lang )#line:129
def record_driving (OOOOO0O0OOOOOO000 ,O0OO00OOOO0OO00O0 ,lang ='en'):#line:131
    _OOO00OOO0000000OO (OOOOO0O0OOOOOO000 ).start (O0OO00OOOO0OO00O0 ,lang )#line:132
