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
    def __init__ (O0OOO0O0O000O000O ,OO0O0000OOO00O0O0 ):#line:14
        O0OOO0O0O000O000O ._robot =OO0O0000OOO00O0O0 #line:15
        O0OOO0O0O000O000O ._q =[[None ,None ,None ,None ],[None ,None ,None ,None ],[None ,None ,None ,None ],[None ,None ,None ,None ]]#line:19
        for O000O0O0O0O000O00 in range (4 ):#line:20
            for O0000O0OOOO00OO00 in range (4 ):#line:21
                O0OOO0O0O000O000O ._q [O000O0O0O0O000O00 ][O0000O0OOOO00OO00 ]={'left':0 ,'right':0 ,'up':0 ,'down':0 }#line:22
        KeyEvent .start ()#line:23
    def wait_space_key (OOO00OO0OOO00O000 ):#line:25
        while True :#line:26
            OO0O000OOOOOOO00O =KeyEvent .get_released_key ()#line:27
            if OO0O000OOOOOOO00O ==KeyEvent .SPACE or OO0O000OOOOOOO00O ==KeyEvent .ESC :#line:28
                return OO0O000OOOOOOO00O #line:29
            elif OO0O000OOOOOOO00O =='r':#line:30
                OOO00OO0OOO00O000 ._robot .reset ()#line:31
            wait (20 )#line:32
    def wait_key (O0O00OO00OOO0O00O ):#line:34
        while True :#line:35
            O00OO0OO00O0OOOOO =KeyEvent .get_released_key ()#line:36
            if O00OO0OO00O0OOOOO ==KeyEvent .SPACE or O00OO0OO00O0OOOOO ==KeyEvent .ESC or O00OO0OO00O0OOOOO =='o'or O00OO0OO00O0OOOOO =='x':#line:37
                return O00OO0OO00O0OOOOO #line:38
            elif O00OO0OO00O0OOOOO =='r':#line:39
                O0O00OO00OOO0O00O ._robot .reset ()#line:40
            wait (20 )#line:41
    def _is_valid_action (OOOO000OO00O00O0O ,OO0OOO00OOO000000 ,O0000OOOO0O0O000O ,OOO0OOOO0000O00O0 ):#line:43
        if OOO0OOOO0000O00O0 ==QWorld ._LEFT :return OO0OOO00OOO000000 >0 #line:44
        elif OOO0OOOO0000O00O0 ==QWorld ._RIGHT :return OO0OOO00OOO000000 <3 #line:45
        elif OOO0OOOO0000O00O0 ==QWorld ._UP :return O0000OOOO0O0O000O <3 #line:46
        else :return O0000OOOO0O0O000O >0 #line:47
    def _is_opposite_action (O0OOO0O00OOO000OO ,O0000OOO0O000O00O ):#line:49
        OOOOOOO0OOOO000O0 =O0OOO0O00OOO000OO ._robot .get_direction ()#line:50
        if O0000OOO0O000O00O ==QWorld ._LEFT :return OOOOOOO0OOOO000O0 ==QWorld ._RIGHT #line:51
        elif O0000OOO0O000O00O ==QWorld ._RIGHT :return OOOOOOO0OOOO000O0 ==QWorld ._LEFT #line:52
        elif O0000OOO0O000O00O ==QWorld ._UP :return OOOOOOO0OOOO000O0 ==QWorld ._DOWN #line:53
        else :return OOOOOOO0OOOO000O0 ==QWorld ._UP #line:54
    def get_max_q_action (O00OOO000OOOO0000 ,OO000OOOOOOO0O0OO ,OOOOO0O0OOO00O00O ):#line:56
        O0OO00OO0OOOO000O =[]#line:57
        OO0O0OO00O0OOOOOO =[]#line:58
        for O0OO0OO000O00OO00 in QWorld ._ACTIONS :#line:59
            if O00OOO000OOOO0000 ._is_valid_action (OO000OOOOOOO0O0OO ,OOOOO0O0OOO00O00O ,O0OO0OO000O00OO00 )and O00OOO000OOOO0000 ._is_opposite_action (O0OO0OO000O00OO00 )==False :#line:60
                O0OO00OO0OOOO000O .append (O00OOO000OOOO0000 ._q [OOOOO0O0OOO00O00O ][OO000OOOOOOO0O0OO ][O0OO0OO000O00OO00 ])#line:61
                OO0O0OO00O0OOOOOO .append (O0OO0OO000O00OO00 )#line:62
        O0O0O0OO0O0O00OOO =max (O0OO00OO0OOOO000O )#line:63
        OO00OO0000O00O000 =[]#line:64
        for O0OO0OO000O00OO00 in OO0O0OO00O0OOOOOO :#line:65
            if O00OOO000OOOO0000 ._q [OOOOO0O0OOO00O00O ][OO000OOOOOOO0O0OO ][O0OO0OO000O00OO00 ]==O0O0O0OO0O0O00OOO :#line:66
                OO00OO0000O00O000 .append (O0OO0OO000O00OO00 )#line:67
        return random .choice (OO00OO0000O00O000 )#line:68
    def get_max_q (O000OOOOO0O0000O0 ,O0O0OO00OOOO000O0 ,O0O00OO000O0O0O00 ):#line:70
        O00O0O0O00O0O000O =[]#line:71
        for O0OOO0OO000000OOO in QWorld ._ACTIONS :#line:72
            if O000OOOOO0O0000O0 ._is_valid_action (O0O0OO00OOOO000O0 ,O0O00OO000O0O0O00 ,O0OOO0OO000000OOO ):#line:73
                O00O0O0O00O0O000O .append (O000OOOOO0O0000O0 ._q [O0O00OO000O0O0O00 ][O0O0OO00OOOO000O0 ][O0OOO0OO000000OOO ])#line:74
        return max (O00O0O0O00O0O000O )#line:75
    def get_next_max_q (O00OOOOO00OO0OOO0 ,OO00000000O000000 ,OOO00OO0OOO000O0O ,O0OOO0O00O0OOOOO0 ):#line:77
        if O00OOOOO00OO0OOO0 ._is_valid_action (OO00000000O000000 ,OOO00OO0OOO000O0O ,O0OOO0O00O0OOOOO0 ):#line:78
            if O0OOO0O00O0OOOOO0 ==QWorld ._LEFT :#line:79
                return O00OOOOO00OO0OOO0 .get_max_q (OO00000000O000000 -1 ,OOO00OO0OOO000O0O )#line:80
            elif O0OOO0O00O0OOOOO0 ==QWorld ._RIGHT :#line:81
                return O00OOOOO00OO0OOO0 .get_max_q (OO00000000O000000 +1 ,OOO00OO0OOO000O0O )#line:82
            elif O0OOO0O00O0OOOOO0 ==QWorld ._UP :#line:83
                return O00OOOOO00OO0OOO0 .get_max_q (OO00000000O000000 ,OOO00OO0OOO000O0O +1 )#line:84
            else :#line:85
                return O00OOOOO00OO0OOO0 .get_max_q (OO00000000O000000 ,OOO00OO0OOO000O0O -1 )#line:86
        return 0 #line:87
    def set_q (O000OOOO0OOOOOO00 ,O000O000O0OOOO0O0 ,OOO0O000OO00O0000 ,OOO000OOO000O0OO0 ,O00OOOOOOOO000O0O ):#line:89
        O000OOOO0OOOOOO00 ._q [OOO0O000OO00O0000 ][O000O000O0OOOO0O0 ][OOO000OOO000O0OO0 ]=O00OOOOOOOO000O0O #line:90
class QGame :#line:93
    def __init__ (O0O0000OO0OO00O0O ):#line:94
        dispose_all ()#line:95
    def start (OOO0OOOO0O00OO0OO ,OO0O00O0OOOOO00O0 ):#line:97
        O0OOOO0O0O0OO00OO =QWorld (OO0O00O0OOOOO00O0 )#line:98
        if O0OOOO0O0O0OO00OO .wait_space_key ()==KeyEvent .ESC :#line:99
            OO0O00O0OOOOO00O0 .dispose ()#line:100
            return #line:101
        O0O00O000OO0O000O =[]#line:103
        O000O000O0000OOOO =0 #line:104
        while True :#line:106
            OO0OOO000O0O000OO =OO0O00O0OOOOO00O0 .get_x ()#line:107
            O000OO0O0OO00O0OO =OO0O00O0OOOOO00O0 .get_y ()#line:108
            OOOOOOOO0O0O0OO0O =O0OOOO0O0O0OO00OO .get_max_q_action (OO0OOO000O0O000OO ,O000OO0O0OO00O0OO )#line:109
            OOO0OOO000O00000O =O0OOOO0O0O0OO00OO .get_next_max_q (OO0OOO000O0O000OO ,O000OO0O0OO00O0OO ,OOOOOOOO0O0O0OO0O )#line:110
            print (OOOOOOOO0O0O0OO0O )#line:112
            OO0O00O0OOOOO00O0 .move (OOOOOOOO0O0O0OO0O )#line:113
            O000O000O0000OOOO +=1 #line:114
            O00OOO0O00O00O00O =O0OOOO0O0O0OO00OO .wait_key ()#line:115
            if O00OOO0O00O00O00O ==KeyEvent .ESC :break #line:116
            OOOO0OO000OO0OOO0 =0 #line:118
            if O00OOO0O00O00O00O =='o':OOOO0OO000OO0OOO0 =1 #line:119
            elif O00OOO0O00O00O00O =='x':OOOO0OO000OO0OOO0 =-1 #line:120
            O0OOOO0O0O0OO00OO .set_q (OO0OOO000O0O000OO ,O000OO0O0OO00O0OO ,OOOOOOOO0O0O0OO0O ,OOOO0OO000OO0OOO0 +0.9 *OOO0OOO000O00000O )#line:122
            if O00OOO0O00O00O00O =='o'or O00OOO0O00O00O00O =='x':#line:123
                if O00OOO0O00O00O00O =='o':#line:124
                    O0O00O000OO0O000O .append (O000O000O0000OOOO )#line:125
                    O000O000O0000OOOO =0 #line:126
                    print (O0O00O000OO0O000O )#line:127
                    OO0O00O0OOOOO00O0 .express_good ()#line:128
                else :#line:129
                    OO0O00O0OOOOO00O0 .express_bad ()#line:130
                OO0O00O0OOOOO00O0 .reset ()#line:131
                if O0OOOO0O0O0OO00OO .wait_space_key ()==KeyEvent .ESC :break #line:132
            wait (20 )#line:134
        OO0O00O0OOOOO00O0 .dispose ()#line:136
def play_q_game_hamster ():#line:139
    QGame ().start (GridHamster (y_axis_up =True ))#line:140
def play_q_game_hamster_s (cross =True ):#line:143
    QGame ().start (GridHamsterS (y_axis_up =True ,cross =cross ))#line:144
