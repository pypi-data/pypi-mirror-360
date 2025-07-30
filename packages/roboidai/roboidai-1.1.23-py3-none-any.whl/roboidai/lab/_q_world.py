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
import random #line:4
class QWorld :#line:7
    _LEFT ='left'#line:8
    _RIGHT ='right'#line:9
    _UP ='up'#line:10
    _DOWN ='down'#line:11
    _ACTIONS =(_LEFT ,_RIGHT ,_UP ,_DOWN )#line:12
    def __init__ (OOOOO0O00OO000OO0 ,O000000O0OOO0OO00 ):#line:14
        OOOOO0O00OO000OO0 ._robot =O000000O0OOO0OO00 #line:15
        OOOOO0O00OO000OO0 ._q =[[None ,None ,None ,None ],[None ,None ,None ,None ],[None ,None ,None ,None ],[None ,None ,None ,None ]]#line:19
        for O000O00000000O00O in range (4 ):#line:20
            for O0O0O00O0O00O00OO in range (4 ):#line:21
                OOOOO0O00OO000OO0 ._q [O000O00000000O00O ][O0O0O00O0O00O00OO ]={'left':0 ,'right':0 ,'up':0 ,'down':0 }#line:22
        KeyEvent .start ()#line:23
    def wait_space_key (OO0O000O000O0OO0O ):#line:25
        while True :#line:26
            O0O0OOOO0OOOOO0OO =KeyEvent .get_released_key ()#line:27
            if O0O0OOOO0OOOOO0OO ==KeyEvent .SPACE or O0O0OOOO0OOOOO0OO ==KeyEvent .ESC :#line:28
                return O0O0OOOO0OOOOO0OO #line:29
            elif O0O0OOOO0OOOOO0OO =='r':#line:30
                OO0O000O000O0OO0O ._robot .reset ()#line:31
            wait (20 )#line:32
    def wait_key (OO0OOOO000O0OO00O ):#line:34
        while True :#line:35
            O0O0OO00OO00O0OOO =KeyEvent .get_released_key ()#line:36
            if O0O0OO00OO00O0OOO ==KeyEvent .SPACE or O0O0OO00OO00O0OOO ==KeyEvent .ESC or O0O0OO00OO00O0OOO =='o'or O0O0OO00OO00O0OOO =='x':#line:37
                return O0O0OO00OO00O0OOO #line:38
            elif O0O0OO00OO00O0OOO =='r':#line:39
                OO0OOOO000O0OO00O ._robot .reset ()#line:40
            wait (20 )#line:41
    def _is_valid_action (OOOOOOOO0OOOOO000 ,O0OOO0O00O00OOO00 ,OOO0OOOOO0000OOOO ,OOOOO0OO00O0O000O ):#line:43
        if OOOOO0OO00O0O000O ==QWorld ._LEFT :return O0OOO0O00O00OOO00 >0 #line:44
        elif OOOOO0OO00O0O000O ==QWorld ._RIGHT :return O0OOO0O00O00OOO00 <3 #line:45
        elif OOOOO0OO00O0O000O ==QWorld ._UP :return OOO0OOOOO0000OOOO <3 #line:46
        else :return OOO0OOOOO0000OOOO >0 #line:47
    def _is_opposite_action (O0OO0O000O0O0000O ,OO0O000OOOO0OOO0O ):#line:49
        O00OO0O000OO0O0OO =O0OO0O000O0O0000O ._robot .get_direction ()#line:50
        if OO0O000OOOO0OOO0O ==QWorld ._LEFT :return O00OO0O000OO0O0OO ==QWorld ._RIGHT #line:51
        elif OO0O000OOOO0OOO0O ==QWorld ._RIGHT :return O00OO0O000OO0O0OO ==QWorld ._LEFT #line:52
        elif OO0O000OOOO0OOO0O ==QWorld ._UP :return O00OO0O000OO0O0OO ==QWorld ._DOWN #line:53
        else :return O00OO0O000OO0O0OO ==QWorld ._UP #line:54
    def get_max_q_action (OOOO00O0OOOO000OO ,O0O000OO0000000OO ,O0O00000O00OO0O0O ):#line:56
        O0O0O00O0OOOOO0O0 =[]#line:57
        O00O0O0O0O00OO0O0 =[]#line:58
        for O000OOOOO00O00OO0 in QWorld ._ACTIONS :#line:59
            if OOOO00O0OOOO000OO ._is_valid_action (O0O000OO0000000OO ,O0O00000O00OO0O0O ,O000OOOOO00O00OO0 )and OOOO00O0OOOO000OO ._is_opposite_action (O000OOOOO00O00OO0 )==False :#line:60
                O0O0O00O0OOOOO0O0 .append (OOOO00O0OOOO000OO ._q [O0O00000O00OO0O0O ][O0O000OO0000000OO ][O000OOOOO00O00OO0 ])#line:61
                O00O0O0O0O00OO0O0 .append (O000OOOOO00O00OO0 )#line:62
        O000OO000OO00OOOO =max (O0O0O00O0OOOOO0O0 )#line:63
        OO0000O00O0OO0OOO =[]#line:64
        for O000OOOOO00O00OO0 in O00O0O0O0O00OO0O0 :#line:65
            if OOOO00O0OOOO000OO ._q [O0O00000O00OO0O0O ][O0O000OO0000000OO ][O000OOOOO00O00OO0 ]==O000OO000OO00OOOO :#line:66
                OO0000O00O0OO0OOO .append (O000OOOOO00O00OO0 )#line:67
        return random .choice (OO0000O00O0OO0OOO )#line:68
    def get_max_q (O0O00OOO00OOO0OOO ,O0OO00O00OO0OOOOO ,OOOO00OO00OO0OOO0 ):#line:70
        O0O00OO000OO0OOO0 =[]#line:71
        for O00OO0O000000O0O0 in QWorld ._ACTIONS :#line:72
            if O0O00OOO00OOO0OOO ._is_valid_action (O0OO00O00OO0OOOOO ,OOOO00OO00OO0OOO0 ,O00OO0O000000O0O0 ):#line:73
                O0O00OO000OO0OOO0 .append (O0O00OOO00OOO0OOO ._q [OOOO00OO00OO0OOO0 ][O0OO00O00OO0OOOOO ][O00OO0O000000O0O0 ])#line:74
        return max (O0O00OO000OO0OOO0 )#line:75
    def get_next_max_q (OO0OOO0OOOOOOOOO0 ,OOOOO000O0OO00OOO ,OO0OOOO00000OO000 ,O0OOOOO0O000OOOOO ):#line:77
        if OO0OOO0OOOOOOOOO0 ._is_valid_action (OOOOO000O0OO00OOO ,OO0OOOO00000OO000 ,O0OOOOO0O000OOOOO ):#line:78
            if O0OOOOO0O000OOOOO ==QWorld ._LEFT :#line:79
                return OO0OOO0OOOOOOOOO0 .get_max_q (OOOOO000O0OO00OOO -1 ,OO0OOOO00000OO000 )#line:80
            elif O0OOOOO0O000OOOOO ==QWorld ._RIGHT :#line:81
                return OO0OOO0OOOOOOOOO0 .get_max_q (OOOOO000O0OO00OOO +1 ,OO0OOOO00000OO000 )#line:82
            elif O0OOOOO0O000OOOOO ==QWorld ._UP :#line:83
                return OO0OOO0OOOOOOOOO0 .get_max_q (OOOOO000O0OO00OOO ,OO0OOOO00000OO000 +1 )#line:84
            else :#line:85
                return OO0OOO0OOOOOOOOO0 .get_max_q (OOOOO000O0OO00OOO ,OO0OOOO00000OO000 -1 )#line:86
        return 0 #line:87
    def set_q (O00OOOOO000OO00OO ,OOO00000O0000OO00 ,OOO0000000O00O000 ,O00O00O000000O00O ,OOOO000OOO0O000O0 ):#line:89
        O00OOOOO000OO00OO ._q [OOO0000000O00O000 ][OOO00000O0000OO00 ][O00O00O000000O00O ]=OOOO000OOO0O000O0 #line:90
class QGame :#line:93
    def __init__ (O0000O00OOOOOO00O ):#line:94
        dispose_all ()#line:95
    def start (O00OO000OOO0OO00O ,OO00OO0000000OOOO ):#line:97
        OOO0OOO00O0OO0O0O =QWorld (OO00OO0000000OOOO )#line:98
        if OOO0OOO00O0OO0O0O .wait_space_key ()==KeyEvent .ESC :#line:99
            OO00OO0000000OOOO .dispose ()#line:100
            return #line:101
        OO0OOO0O0000O0O0O =[]#line:103
        O0O00OO00000O000O =0 #line:104
        while True :#line:106
            OOOOOO0O0O000OO00 =OO00OO0000000OOOO .get_x ()#line:107
            O00OO00000000OOO0 =OO00OO0000000OOOO .get_y ()#line:108
            O0OOOO000O000O000 =OOO0OOO00O0OO0O0O .get_max_q_action (OOOOOO0O0O000OO00 ,O00OO00000000OOO0 )#line:109
            OOO0OOO0OOO000O0O =OOO0OOO00O0OO0O0O .get_next_max_q (OOOOOO0O0O000OO00 ,O00OO00000000OOO0 ,O0OOOO000O000O000 )#line:110
            print (O0OOOO000O000O000 )#line:112
            OO00OO0000000OOOO .move (O0OOOO000O000O000 )#line:113
            O0O00OO00000O000O +=1 #line:114
            OO0OOO0OO0O0O000O =OOO0OOO00O0OO0O0O .wait_key ()#line:115
            if OO0OOO0OO0O0O000O ==KeyEvent .ESC :break #line:116
            OOOO0OOO0O0OOOOOO =0 #line:118
            if OO0OOO0OO0O0O000O =='o':OOOO0OOO0O0OOOOOO =1 #line:119
            elif OO0OOO0OO0O0O000O =='x':OOOO0OOO0O0OOOOOO =-1 #line:120
            OOO0OOO00O0OO0O0O .set_q (OOOOOO0O0O000OO00 ,O00OO00000000OOO0 ,O0OOOO000O000O000 ,OOOO0OOO0O0OOOOOO +0.9 *OOO0OOO0OOO000O0O )#line:122
            if OO0OOO0OO0O0O000O =='o'or OO0OOO0OO0O0O000O =='x':#line:123
                if OO0OOO0OO0O0O000O =='o':#line:124
                    OO0OOO0O0000O0O0O .append (O0O00OO00000O000O )#line:125
                    O0O00OO00000O000O =0 #line:126
                    print (OO0OOO0O0000O0O0O )#line:127
                    OO00OO0000000OOOO .express_good ()#line:128
                else :#line:129
                    OO00OO0000000OOOO .express_bad ()#line:130
                OO00OO0000000OOOO .reset ()#line:131
                if OOO0OOO00O0OO0O0O .wait_space_key ()==KeyEvent .ESC :break #line:132
            wait (20 )#line:134
        OO00OO0000000OOOO .dispose ()#line:136
def play_q_game_hamster ():#line:139
    QGame ().start (GridHamster (y_axis_up =True ))#line:140
def play_q_game_hamster_s (cross =True ):#line:143
    QGame ().start (GridHamsterS (y_axis_up =True ,cross =cross ))#line:144
