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
from roboidai ._lang import translate #line:6
class _OO00OO0OOO00O000O :#line:9
    _STATE_IDLE =0 #line:10
    _STATE_MOVE =1 #line:11
    def _usage (O0OO000O0O0OOOO0O ,lang ='en'):#line:13
        print (translate ('lab._line_tracer.usage',lang ))#line:14
    def start (OO0O0OOOOOOOOOOO0 ,O0OO0O0O00OOO00O0 ,lang ='en'):#line:16
        OO0O0OOOOOOOOOOO0 ._usage (lang )#line:17
        KeyEvent .start ()#line:18
class _O00O0O0O0O000OOOO (_OO00OO0OOO00O000O ):#line:21
    def _save (OO00O0O00000O0OOO ,O00OOOO0OO0O0OOO0 ,OO00OO000OOOOO0OO ):#line:22
        if isinstance (OO00OO000OOOOO0OO ,str ):#line:23
            O0O0OOOO00OOOO000 =os .path .dirname (OO00OO000OOOOO0OO )#line:24
            if not os .path .isdir (O0O0OOOO00OOOO000 ):#line:25
                os .makedirs (O0O0OOOO00OOOO000 )#line:26
        O00OOOO0OO0O0OOO0 .to_csv (OO00OO000OOOOO0OO ,index =False )#line:27
    def start (OOO0OOO0O00OOOOOO ,O000000OO00O0OOOO ,OO0O00O0000OOO00O ,sensor ='left',lang ='en'):#line:29
        super (_O00O0O0O0O000OOOO ,OOO0OOO0O00OOOOOO ).start (OO0O00O0000OOO00O ,lang )#line:30
        if O000000OO00O0OOOO is None :#line:32
            KeyEvent .stop ()#line:33
            return #line:34
        O00O00O0O000OOOO0 =[]#line:36
        O00OOOO0O0O00O00O =[]#line:37
        O0OOOOOOO0OO00O0O =[]#line:38
        O0OO0OO0OOO0OOO00 =[]#line:39
        OO0OO000OO00OO000 =_OO00OO0OOO00O000O ._STATE_IDLE #line:40
        OOOO0O0OO0OOOOOO0 =0 #line:41
        OOO0O00O00OOOOO0O =False #line:42
        while True :#line:44
            O00O000O00OO0OOO0 =KeyEvent .get_released_key ()#line:45
            if OO0OO000OO00OO000 ==_OO00OO0OOO00O000O ._STATE_IDLE :#line:46
                if O00O000O00OO0OOO0 ==KeyEvent .SPACE :#line:47
                    OO0OO000OO00OO000 =_OO00OO0OOO00O000O ._STATE_MOVE #line:48
                    OOOO00O0OO0OO00OO =[]#line:49
                    O0OO0O00OO0O0OO0O =[]#line:50
                    O00O0O0000O00OOOO =[]#line:51
                    O0000O0O0O0O00OO0 =[]#line:52
            elif OO0OO000OO00OO000 ==_OO00OO0OOO00O000O ._STATE_MOVE :#line:53
                if sensor =='left':#line:54
                    OOO000OO0OOOO0OOO =(O0O00OOO00OOOO0O0 -50 )*0.5 #line:55
                elif sensor =='right':#line:56
                    OOO000OO0OOOO0OOO =(50 -O00O00OOO0O0000OO )*0.5 #line:57
                else :#line:58
                    OOO000OO0OOOO0OOO =(O0O00OOO00OOOO0O0 -O00O00OOO0O0000OO )*0.5 #line:59
                OOO00O0OOO0O00000 =30 +OOO000OO0OOOO0OOO #line:60
                OOO00OOOO0O0OOO00 =30 -OOO000OO0OOOO0OOO #line:61
                O000000OO00O0OOOO .wheels (OOO00O0OOO0O00000 ,OOO00OOOO0O0OOO00 )#line:62
                if OOO0O00O00OOOOO0O :#line:63
                    OOOO00O0OO0OO00OO .append (O000000OO00O0OOOO .left_floor ())#line:64
                    O0OO0O00OO0O0OO0O .append (O000000OO00O0OOOO .right_floor ())#line:65
                    O00O0O0000O00OOOO .append (OOO00O0OOO0O00000 )#line:66
                    O0000O0O0O0O00OO0 .append (OOO00OOOO0O0OOO00 )#line:67
                if O0O00OOO00OOOO0O0 <30 and O00O00OOO0O0000OO <30 :#line:69
                    OOOO0O0OO0OOOOOO0 +=1 #line:70
                    OOO0O00O00OOOOO0O =False #line:71
                    if OOOO0O0OO0OOOOOO0 >3 :#line:72
                        O000000OO00O0OOOO .stop ()#line:73
                        OO0OO000OO00OO000 =_OO00OO0OOO00O000O ._STATE_IDLE #line:74
                        OOOO0O0OO0OOOOOO0 =0 #line:75
                        O00O00O0O000OOOO0 .extend (OOOO00O0OO0OO00OO [20 :-20 ])#line:76
                        O00OOOO0O0O00O00O .extend (O0OO0O00OO0O0OO0O [20 :-20 ])#line:77
                        O0OOOOOOO0OO00O0O .extend (O00O0O0000O00OOOO [20 :-20 ])#line:78
                        O0OO0OO0OOO0OOO00 .extend (O0000O0O0O0O00OO0 [20 :-20 ])#line:79
                else :#line:80
                    OOOO0O0OO0OOOOOO0 =0 #line:81
                    OOO0O00O00OOOOO0O =True #line:82
            O0O00OOO00OOOO0O0 =O000000OO00O0OOOO .left_floor ()#line:84
            O00O00OOO0O0000OO =O000000OO00O0OOOO .right_floor ()#line:85
            if O00O000O00OO0OOO0 ==KeyEvent .ESC :#line:86
                if sensor =='left':#line:87
                    O0000OOOO00000000 =pd .DataFrame ({'left_floor':O00O00O0O000OOOO0 ,'left_wheel':O0OOOOOOO0OO00O0O ,'right_wheel':O0OO0OO0OOO0OOO00 })#line:90
                elif sensor =='right':#line:91
                    O0000OOOO00000000 =pd .DataFrame ({'right_floor':O00OOOO0O0O00O00O ,'left_wheel':O0OOOOOOO0OO00O0O ,'right_wheel':O0OO0OO0OOO0OOO00 })#line:94
                else :#line:95
                    O0000OOOO00000000 =pd .DataFrame ({'left_floor':O00O00O0O000OOOO0 ,'right_floor':O00OOOO0O0O00O00O ,'left_wheel':O0OOOOOOO0OO00O0O ,'right_wheel':O0OO0OO0OOO0OOO00 })#line:99
                OOO0OOO0O00OOOOOO ._save (O0000OOOO00000000 ,OO0O00O0000OOO00O )#line:100
                print (translate ('lab._line_tracer.saved',lang ).format (OO0O00O0000OOO00O ))#line:101
                wait (1000 )#line:102
                break #line:103
            wait (20 )#line:105
        KeyEvent .stop ()#line:107
        O000000OO00O0OOOO .dispose ()#line:108
def collect_driving_data (OO0OOO00O0OOO0O00 ,O00OO0OO0OOOOOOO0 ,sensor ='all',lang ='en'):#line:111
    if isinstance (OO0OOO00O0OOO0O00 ,Hamster )or isinstance (OO0OOO00O0OOO0O00 ,HamsterS ):#line:112
        _O00O0O0O0O000OOOO ().start (OO0OOO00O0OOO0O00 ,O00OO0OO0OOOOOOO0 ,sensor ,lang )#line:113
