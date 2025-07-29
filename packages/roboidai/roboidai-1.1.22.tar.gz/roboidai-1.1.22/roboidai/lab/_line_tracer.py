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
class _O00O0O0O000OOO0OO :#line:9
    _STATE_IDLE =0 #line:10
    _STATE_MOVE =1 #line:11
    def _usage (OO000O0000O0OOOO0 ,lang ='en'):#line:13
        print (translate ('lab._line_tracer.usage',lang ))#line:14
    def start (OO0000O0O0O000O0O ,OO00OOO0OOO00000O ,lang ='en'):#line:16
        OO0000O0O0O000O0O ._usage (lang )#line:17
        KeyEvent .start ()#line:18
class _O0OOO0O0OO0OOOOO0 (_O00O0O0O000OOO0OO ):#line:21
    def _save (O000O0O0OO0O0O000 ,OOO0OO0O0O00OOO00 ,O00O0O0O0OO00000O ):#line:22
        if isinstance (O00O0O0O0OO00000O ,str ):#line:23
            OOOOO000000OOO000 =os .path .dirname (O00O0O0O0OO00000O )#line:24
            if not os .path .isdir (OOOOO000000OOO000 ):#line:25
                os .makedirs (OOOOO000000OOO000 )#line:26
        OOO0OO0O0O00OOO00 .to_csv (O00O0O0O0OO00000O ,index =False )#line:27
    def start (OOO0O000O0OOOO00O ,OO0O0O00O0OOOO00O ,O00O000OO0O0O0OO0 ,sensor ='left',lang ='en'):#line:29
        super (_O0OOO0O0OO0OOOOO0 ,OOO0O000O0OOOO00O ).start (O00O000OO0O0O0OO0 ,lang )#line:30
        if OO0O0O00O0OOOO00O is None :#line:32
            KeyEvent .stop ()#line:33
            return #line:34
        OO0O0OO0O00O00O0O =[]#line:36
        O00O0000OO0O0OO0O =[]#line:37
        OOOO0O000O00O0O0O =[]#line:38
        O00OO0O0OO000O0O0 =[]#line:39
        O0OO00O0O0OOOOO00 =_O00O0O0O000OOO0OO ._STATE_IDLE #line:40
        O0O0OO0OO00OOOO00 =0 #line:41
        O00000O0000O0O000 =False #line:42
        while True :#line:44
            O000O00O00O00OOOO =KeyEvent .get_released_key ()#line:45
            if O0OO00O0O0OOOOO00 ==_O00O0O0O000OOO0OO ._STATE_IDLE :#line:46
                if O000O00O00O00OOOO ==KeyEvent .SPACE :#line:47
                    O0OO00O0O0OOOOO00 =_O00O0O0O000OOO0OO ._STATE_MOVE #line:48
                    O0O0O000O0OO0OOO0 =[]#line:49
                    O00OO0O00000OO000 =[]#line:50
                    O000O0OOOO000O0O0 =[]#line:51
                    OO00000O00O0OOOOO =[]#line:52
            elif O0OO00O0O0OOOOO00 ==_O00O0O0O000OOO0OO ._STATE_MOVE :#line:53
                if sensor =='left':#line:54
                    O0OO0000OOO0000OO =(OOO00O0OOO0000OO0 -50 )*0.5 #line:55
                elif sensor =='right':#line:56
                    O0OO0000OOO0000OO =(50 -OOO00O0OOO00000OO )*0.5 #line:57
                else :#line:58
                    O0OO0000OOO0000OO =(OOO00O0OOO0000OO0 -OOO00O0OOO00000OO )*0.5 #line:59
                O000OO0OOO00OOO0O =30 +O0OO0000OOO0000OO #line:60
                O00O0OOO0000000O0 =30 -O0OO0000OOO0000OO #line:61
                OO0O0O00O0OOOO00O .wheels (O000OO0OOO00OOO0O ,O00O0OOO0000000O0 )#line:62
                if O00000O0000O0O000 :#line:63
                    O0O0O000O0OO0OOO0 .append (OO0O0O00O0OOOO00O .left_floor ())#line:64
                    O00OO0O00000OO000 .append (OO0O0O00O0OOOO00O .right_floor ())#line:65
                    O000O0OOOO000O0O0 .append (O000OO0OOO00OOO0O )#line:66
                    OO00000O00O0OOOOO .append (O00O0OOO0000000O0 )#line:67
                if OOO00O0OOO0000OO0 <30 and OOO00O0OOO00000OO <30 :#line:69
                    O0O0OO0OO00OOOO00 +=1 #line:70
                    O00000O0000O0O000 =False #line:71
                    if O0O0OO0OO00OOOO00 >3 :#line:72
                        OO0O0O00O0OOOO00O .stop ()#line:73
                        O0OO00O0O0OOOOO00 =_O00O0O0O000OOO0OO ._STATE_IDLE #line:74
                        O0O0OO0OO00OOOO00 =0 #line:75
                        OO0O0OO0O00O00O0O .extend (O0O0O000O0OO0OOO0 [20 :-20 ])#line:76
                        O00O0000OO0O0OO0O .extend (O00OO0O00000OO000 [20 :-20 ])#line:77
                        OOOO0O000O00O0O0O .extend (O000O0OOOO000O0O0 [20 :-20 ])#line:78
                        O00OO0O0OO000O0O0 .extend (OO00000O00O0OOOOO [20 :-20 ])#line:79
                else :#line:80
                    O0O0OO0OO00OOOO00 =0 #line:81
                    O00000O0000O0O000 =True #line:82
            OOO00O0OOO0000OO0 =OO0O0O00O0OOOO00O .left_floor ()#line:84
            OOO00O0OOO00000OO =OO0O0O00O0OOOO00O .right_floor ()#line:85
            if O000O00O00O00OOOO ==KeyEvent .ESC :#line:86
                if sensor =='left':#line:87
                    O0O000OOOOOOO000O =pd .DataFrame ({'left_floor':OO0O0OO0O00O00O0O ,'left_wheel':OOOO0O000O00O0O0O ,'right_wheel':O00OO0O0OO000O0O0 })#line:90
                elif sensor =='right':#line:91
                    O0O000OOOOOOO000O =pd .DataFrame ({'right_floor':O00O0000OO0O0OO0O ,'left_wheel':OOOO0O000O00O0O0O ,'right_wheel':O00OO0O0OO000O0O0 })#line:94
                else :#line:95
                    O0O000OOOOOOO000O =pd .DataFrame ({'left_floor':OO0O0OO0O00O00O0O ,'right_floor':O00O0000OO0O0OO0O ,'left_wheel':OOOO0O000O00O0O0O ,'right_wheel':O00OO0O0OO000O0O0 })#line:99
                OOO0O000O0OOOO00O ._save (O0O000OOOOOOO000O ,O00O000OO0O0O0OO0 )#line:100
                print (translate ('lab._line_tracer.saved',lang ).format (O00O000OO0O0O0OO0 ))#line:101
                wait (1000 )#line:102
                break #line:103
            wait (20 )#line:105
        KeyEvent .stop ()#line:107
        OO0O0O00O0OOOO00O .dispose ()#line:108
def collect_driving_data (O00O0O000000000OO ,O0OOOO0000O0OOO0O ,sensor ='all',lang ='en'):#line:111
    if isinstance (O00O0O000000000OO ,Hamster )or isinstance (O00O0O000000000OO ,HamsterS ):#line:112
        _O0OOO0O0OO0OOOOO0 ().start (O00O0O000000000OO ,O0OOOO0000O0OOO0O ,sensor ,lang )#line:113
