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
_O000O0OOO00OO0OO0 ={'en':{'usage':'Press space key to move.\nPress s key to save.\nPress ESC key to quit.\n','saved':'Saved to {}'},'ko':{'usage':'스페이스 키를 누르면 이동합니다.\ns키를 누르면 저장합니다.\nESC 키를 누르면 종료합니다.\n','saved':'{}에 저장되었습니다.'}}#line:17
class _O0O0000OO0O00OO0O :#line:20
    _STATE_IDLE =0 #line:21
    _STATE_MOVE =1 #line:22
    def _usage (OO00O0O00OOO0000O ,lang ='en'):#line:24
        print (_O000O0OOO00OO0OO0 [lang ]['usage'])#line:25
    def start (OOO0OO00OO00O000O ,OO00O0OO0OOO0O000 ,lang ='en'):#line:27
        OOO0OO00OO00O000O ._usage (lang )#line:28
        KeyEvent .start ()#line:29
class _O000O0OO0000O0OOO (_O0O0000OO0O00OO0O ):#line:32
    def _create_robot (OO0OO0O0O0OO00OO0 ):#line:33
        return None #line:34
    def _save (OO00OO00O00OO000O ,OO0O0OO00O0OOOOOO ,O0O00OOOO00OO0OO0 ):#line:36
        if isinstance (O0O00OOOO00OO0OO0 ,str ):#line:37
            O00000O00000O0000 =os .path .dirname (O0O00OOOO00OO0OO0 )#line:38
            if not os .path .isdir (O00000O00000O0000 ):#line:39
                os .makedirs (O00000O00000O0000 )#line:40
        OO0O0OO00O0OOOOOO .to_csv (O0O00OOOO00OO0OO0 ,index =False )#line:41
    def start (O000O0000O00OO000 ,OOOO000OOOO0O000O ,lang ='en'):#line:43
        super (_O000O0OO0000O0OOO ,O000O0000O00OO000 ).start (OOOO000OOOO0O000O ,lang )#line:44
        O0OO0OO0OO0O0OOO0 =O000O0000O00OO000 ._create_robot ()#line:46
        if O0OO0OO0OO0O0OOO0 is None :#line:47
            KeyEvent .stop ()#line:48
            return #line:49
        O0OOOOO00OOOO0OOO =[]#line:51
        OOOO00000O0OO0OO0 =[]#line:52
        OO00O0O00000OOOO0 =[]#line:53
        O0OOOOOOOOOO00O00 =_O0O0000OO0O00OO0O ._STATE_IDLE #line:54
        O0O0OOOO000OOOOO0 =0 #line:55
        OOO0000O0O0000O0O =False #line:56
        while True :#line:58
            OOO0O00OOOO0O000O =KeyEvent .get_released_key ()#line:59
            if O0OOOOOOOOOO00O00 ==_O0O0000OO0O00OO0O ._STATE_IDLE :#line:60
                if OOO0O00OOOO0O000O ==KeyEvent .SPACE :#line:61
                    O0OOOOOOOOOO00O00 =_O0O0000OO0O00OO0O ._STATE_MOVE #line:62
                    O0OO00OO0000O000O =[]#line:63
                    O0OOO00000OO00OOO =[]#line:64
                    O00OO00OOO00OOOO0 =[]#line:65
            elif O0OOOOOOOOOO00O00 ==_O0O0000OO0O00OO0O ._STATE_MOVE :#line:66
                OO000O0OO0O00O0O0 =(O0O0OOOO000OOOO0O -50 )*0.5 #line:67
                O0O0OO0O00OOOO0O0 =30 +OO000O0OO0O00O0O0 #line:68
                OO000OO00O0O0OOOO =30 -OO000O0OO0O00O0O0 #line:69
                O0OO0OO0OO0O0OOO0 .wheels (O0O0OO0O00OOOO0O0 ,OO000OO00O0O0OOOO )#line:70
                if OOO0000O0O0000O0O :#line:71
                    O0OO00OO0000O000O .append (O0OO0OO0OO0O0OOO0 .left_floor ())#line:72
                    O0OOO00000OO00OOO .append (O0O0OO0O00OOOO0O0 )#line:73
                    O00OO00OOO00OOOO0 .append (OO000OO00O0O0OOOO )#line:74
                if O0O0OOOO000OOOO0O <30 and O0O0OOOO00000000O <30 :#line:76
                    O0O0OOOO000OOOOO0 +=1 #line:77
                    OOO0000O0O0000O0O =False #line:78
                    if O0O0OOOO000OOOOO0 >3 :#line:79
                        O0OO0OO0OO0O0OOO0 .stop ()#line:80
                        O0OOOOOOOOOO00O00 =_O0O0000OO0O00OO0O ._STATE_IDLE #line:81
                        O0O0OOOO000OOOOO0 =0 #line:82
                        O0OOOOO00OOOO0OOO .extend (O0OO00OO0000O000O [20 :-20 ])#line:83
                        OOOO00000O0OO0OO0 .extend (O0OOO00000OO00OOO [20 :-20 ])#line:84
                        OO00O0O00000OOOO0 .extend (O00OO00OOO00OOOO0 [20 :-20 ])#line:85
                else :#line:86
                    O0O0OOOO000OOOOO0 =0 #line:87
                    OOO0000O0O0000O0O =True #line:88
            O0O0OOOO000OOOO0O =O0OO0OO0OO0O0OOO0 .left_floor ()#line:90
            O0O0OOOO00000000O =O0OO0OO0OO0O0OOO0 .right_floor ()#line:91
            if OOO0O00OOOO0O000O =='s':#line:92
                OOO00OO0O0O00O000 =pd .DataFrame ({'left_floor':O0OOOOO00OOOO0OOO ,'left_wheel':OOOO00000O0OO0OO0 ,'right_wheel':OO00O0O00000OOOO0 })#line:95
                O000O0000O00OO000 ._save (OOO00OO0O0O00O000 ,OOOO000OOOO0O000O )#line:96
                print (_O000O0OOO00OO0OO0 [lang ]['saved'].format (OOOO000OOOO0O000O ))#line:97
            elif OOO0O00OOOO0O000O ==KeyEvent .ESC :#line:98
                break #line:99
            wait (20 )#line:101
        KeyEvent .stop ()#line:103
        O0OO0OO0OO0O0OOO0 .dispose ()#line:104
class _O00O0O00O0OO0O000 (_O000O0OO0000O0OOO ):#line:107
    def _create_robot (O0O000OOOO0OOOOO0 ):#line:108
        return Hamster ()#line:109
class _OO00O0O000O000OO0 (_O000O0OO0000O0OOO ):#line:112
    def _create_robot (O000OO000O0O000OO ):#line:113
        return HamsterS ()#line:114
class _O00O00O0000OO0O0O (_O000O0OO0000O0OOO ):#line:117
    def __init__ (OO0OOO0O0OO0O000O ,O0OO0O0O0O0O00000 ):#line:118
        OO0OOO0O0OO0O000O ._robot =O0OO0O0O0O0O00000 #line:119
    def _create_robot (OO0000OOOO00O0OOO ):#line:121
        return OO0000OOOO00O0OOO ._robot #line:122
def record_hamster (O00OO00O000O0O000 ,lang ='en'):#line:125
    _O00O0O00O0OO0O000 ().start (O00OO00O000O0O000 ,lang )#line:126
def record_hamster_s (OO0O00O0O000O0O00 ,lang ='en'):#line:128
    _OO00O0O000O000OO0 ().start (OO0O00O0O000O0O00 ,lang )#line:129
def record_driving (O0OOO0O0OO0O000OO ,O0OOOOOOO0O000O00 ,lang ='en'):#line:131
    _O00O00O0000OO0O0O (O0OOO0O0OO0O000OO ).start (O0OOOOOOO0O000O00 ,lang )#line:132
