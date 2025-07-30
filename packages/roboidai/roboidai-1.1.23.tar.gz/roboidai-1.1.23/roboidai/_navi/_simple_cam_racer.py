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
class SimpleCamRacer :#line:6
    _LEFT =1 #line:7
    _RIGHT =2 #line:8
    _RED =3 #line:9
    _GREEN =4 #line:10
    _BLUE =5 #line:11
    _BLOBS ={'left':1 ,'right':2 ,'red':3 ,'green':4 ,'blue':5 }#line:18
    _COLORS ={'red':3 ,'green':4 ,'blue':5 }#line:23
    def __init__ (OOOOO00O0OOO00O0O ,red_h_range =(0 ,10 ,170 ,180 ),green_h_range =(40 ,80 ),blue_h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 ),lane_window_height =50 ):#line:25
        OOOOO00O0OOO00O0O ._h_range ={SimpleCamRacer ._RED :red_h_range ,SimpleCamRacer ._GREEN :green_h_range ,SimpleCamRacer ._BLUE :blue_h_range }#line:30
        OOOOO00O0OOO00O0O ._s_range =s_range #line:31
        OOOOO00O0OOO00O0O ._v_range =v_range #line:32
        OOOOO00O0OOO00O0O ._lane_window_height =lane_window_height #line:33
        OOOOO00O0OOO00O0O ._direction =1 #line:34
        OOOOO00O0OOO00O0O ._speed =50 #line:35
        OOOOO00O0OOO00O0O ._gain =0.1 #line:36
        OOOOO00O0OOO00O0O ._left_velocity =0 #line:37
        OOOOO00O0OOO00O0O ._right_velocity =0 #line:38
        OOOOO00O0OOO00O0O ._results ={}#line:39
        OOOOO00O0OOO00O0O ._clear ()#line:40
        OOOOO00O0OOO00O0O .set_lane_colors ('green','blue')#line:41
    def _clear (OO0O0O0OOO0O00000 ):#line:43
        OO0O0O0OOO0O00000 ._results [SimpleCamRacer ._LEFT ]=None #line:44
        OO0O0O0OOO0O00000 ._results [SimpleCamRacer ._RIGHT ]=None #line:45
        OO0O0O0OOO0O00000 ._results [SimpleCamRacer ._RED ]=None #line:46
        OO0O0O0OOO0O00000 ._results [SimpleCamRacer ._GREEN ]=None #line:47
        OO0O0O0OOO0O00000 ._results [SimpleCamRacer ._BLUE ]=None #line:48
    def _find_blob (OOO0000000OOO00OO ,OOOOOO0OO00O0000O ,OOO00O0O0OO00OOO0 ,OO0O00OOO00O0OO0O ,O0OO00OO00O000O0O ,O00OOO0O0OO0000O0 ,OO0O0O00O0O0OO00O ,O000O0000OO0OOOO0 ,O0O000O0O0O00OOO0 ):#line:50
        O00OO0OOO0OO0000O =OOOOOO0OO00O0000O [O000O0000OO0OOOO0 :O0O000O0O0O00OOO0 ,O00OOO0O0OO0000O0 :OO0O0O00O0O0OO00O ]#line:51
        OO0OOOOO0OOO00O00 =cv2 .cvtColor (O00OO0OOO0OO0000O ,cv2 .COLOR_BGR2HSV )#line:52
        O0OO00000O0O00OO0 =cv2 .inRange (OO0OOOOO0OOO00O00 ,(OOO00O0O0OO00OOO0 [0 ],OO0O00OOO00O0OO0O [0 ],O0OO00OO00O000O0O [0 ]),(OOO00O0O0OO00OOO0 [1 ],OO0O00OOO00O0OO0O [1 ],O0OO00OO00O000O0O [1 ]))#line:54
        if len (OOO00O0O0OO00OOO0 )>=4 :#line:55
            O0OO00000O0O00OO0 |=cv2 .inRange (OO0OOOOO0OOO00O00 ,(OOO00O0O0OO00OOO0 [2 ],OO0O00OOO00O0OO0O [0 ],O0OO00OO00O000O0O [0 ]),(OOO00O0O0OO00OOO0 [3 ],OO0O00OOO00O0OO0O [1 ],O0OO00OO00O000O0O [1 ]))#line:56
        O0OO0O00O000O00O0 =np .ones ((3 ,3 ),np .uint8 )#line:58
        O0OO00000O0O00OO0 =cv2 .morphologyEx (O0OO00000O0O00OO0 ,cv2 .MORPH_OPEN ,O0OO0O00O000O00O0 )#line:59
        O0OO00000O0O00OO0 =cv2 .morphologyEx (O0OO00000O0O00OO0 ,cv2 .MORPH_CLOSE ,O0OO0O00O000O00O0 )#line:60
        OOO0OO0O00OO000O0 ,_O00O0O0O0OO0OO00O =cv2 .findContours (O0OO00000O0O00OO0 ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:62
        OO0OOOOO0O0O0O0OO =[cv2 .contourArea (O000OOO0000OOO00O )for O000OOO0000OOO00O in OOO0OO0O00OO000O0 ]#line:63
        if OO0OOOOO0O0O0O0OO :#line:64
            O0OOO000OO00O00O0 =np .argmax (OO0OOOOO0O0O0O0OO )#line:65
            O00O0OO0OOO0OOO0O =int (OO0OOOOO0O0O0O0OO [O0OOO000OO00O00O0 ])#line:66
            if O00O0OO0OOO0OOO0O >5 :#line:67
                OOO000O0OO0OO0OO0 =OOO0OO0O00OO000O0 [O0OOO000OO00O00O0 ]#line:68
                OOO00OOOO00OO0O00 ,O0O00O0O000OO0OOO ,O0O0O000O000OOOO0 ,OO0OO0OOO00OOO000 =cv2 .boundingRect (OOO000O0OO0OO0OO0 )#line:69
                OOOO0000000OO000O ={'box':(OOO00OOOO00OO0O00 +O00OOO0O0OO0000O0 ,O0O00O0O000OO0OOO +O000O0000OO0OOOO0 ,OOO00OOOO00OO0O00 +O0O0O000O000OOOO0 +O00OOO0O0OO0000O0 ,O0O00O0O000OO0OOO +OO0OO0OOO00OOO000 +O000O0000OO0OOOO0 ),'width':O0O0O000O000OOOO0 ,'height':OO0OO0OOO00OOO000 ,'area':O0O0O000O000OOOO0 *OO0OO0OOO00OOO000 ,'pixels':O00O0OO0OOO0OOO0O }#line:76
                OO000000OOO0O00OO =cv2 .moments (OOO000O0OO0OO0OO0 )#line:77
                OO000O000OO00OOO0 =OO000000OOO0O00OO ['m00']#line:78
                if OO000O000OO00OOO0 >0 :#line:79
                    OOOO0000000OO000O ['xy']=(int (OO000000OOO0O00OO ['m10']/OO000O000OO00OOO0 )+O00OOO0O0OO0000O0 ,int (OO000000OOO0O00OO ['m01']/OO000O000OO00OOO0 )+O000O0000OO0OOOO0 )#line:80
                    return OOOO0000000OO000O #line:81
        return None #line:82
    def _find_color (O0000O0O00OOO0000 ,OO00OO0O0OOO0O00O ,OOO0O000OOO0OO00O ,OO0O0O00O00O0OO00 ,OOO0OOOOO0000OO00 ,OO000OOOOOO0O0O00 ,O0000O00O00O0O00O ):#line:84
        OOOOO0O0OO000OO0O =O0000O0O00OOO0000 ._h_range [OOO0O000OOO0OO00O ]#line:85
        O0OO0OOOOOOOO000O =O0000O0O00OOO0000 ._s_range #line:86
        O0O0O000O0O0O000O =O0000O0O00OOO0000 ._v_range #line:87
        if O0000O0O00OOO0000 ._left_lane_color ==OOO0O000OOO0OO00O and O0000O0O00OOO0000 ._right_lane_color ==OOO0O000OOO0OO00O :#line:89
            O00O0O0O00OO0000O =O0000O0O00OOO0000 ._find_blob (OO00OO0O0OOO0O00O ,OOOOO0O0OO000OO0O ,O0OO0OOOOOOOO000O ,O0O0O000O0O0O000O ,0 ,OO000OOOOOO0O0O00 ,O0000O00O00O0O00O ,OOO0OOOOO0000OO00 )#line:90
            O0OOOOO0OO0000O0O =O0000O0O00OOO0000 ._find_blob (OO00OO0O0OOO0O00O ,OOOOO0O0OO000OO0O ,O0OO0OOOOOOOO000O ,O0O0O000O0O0O000O ,OO000OOOOOO0O0O00 ,OO0O0O00O00O0OO00 ,O0000O00O00O0O00O ,OOO0OOOOO0000OO00 )#line:91
            if O00O0O0O00OO0000O is not None and O0OOOOO0OO0000O0O is not None :#line:92
                O0000O0O00OOO0000 ._results [OOO0O000OOO0OO00O ]=O0OOOOO0OO0000O0O if O0OOOOO0OO0000O0O ['pixels']>O00O0O0O00OO0000O ['pixels']else O00O0O0O00OO0000O #line:93
                O0000O0O00OOO0000 ._results [SimpleCamRacer ._LEFT ]=O00O0O0O00OO0000O #line:94
                O0000O0O00OOO0000 ._results [SimpleCamRacer ._RIGHT ]=O0OOOOO0OO0000O0O #line:95
            elif O00O0O0O00OO0000O is not None :#line:96
                O0000O0O00OOO0000 ._results [OOO0O000OOO0OO00O ]=O00O0O0O00OO0000O #line:97
                O0000O0O00OOO0000 ._results [SimpleCamRacer ._LEFT ]=O00O0O0O00OO0000O #line:98
            elif O0OOOOO0OO0000O0O is not None :#line:99
                O0000O0O00OOO0000 ._results [OOO0O000OOO0OO00O ]=O0OOOOO0OO0000O0O #line:100
                O0000O0O00OOO0000 ._results [SimpleCamRacer ._RIGHT ]=O0OOOOO0OO0000O0O #line:101
            else :#line:102
                O0000O0O00OOO0000 ._results [OOO0O000OOO0OO00O ]=None #line:103
        elif O0000O0O00OOO0000 ._left_lane_color ==OOO0O000OOO0OO00O :#line:104
            OO0OO00O00O0O0O00 =O0000O0O00OOO0000 ._find_blob (OO00OO0O0OOO0O00O ,OOOOO0O0OO000OO0O ,O0OO0OOOOOOOO000O ,O0O0O000O0O0O000O ,0 ,OO0O0O00O00O0OO00 ,O0000O00O00O0O00O ,OOO0OOOOO0000OO00 )#line:105
            O0000O0O00OOO0000 ._results [OOO0O000OOO0OO00O ]=OO0OO00O00O0O0O00 #line:106
            if OO0OO00O00O0O0O00 is not None :#line:107
                O0000O0O00OOO0000 ._results [SimpleCamRacer ._LEFT ]=OO0OO00O00O0O0O00 #line:108
        elif O0000O0O00OOO0000 ._right_lane_color ==OOO0O000OOO0OO00O :#line:109
            OO0OO00O00O0O0O00 =O0000O0O00OOO0000 ._find_blob (OO00OO0O0OOO0O00O ,OOOOO0O0OO000OO0O ,O0OO0OOOOOOOO000O ,O0O0O000O0O0O000O ,0 ,OO0O0O00O00O0OO00 ,O0000O00O00O0O00O ,OOO0OOOOO0000OO00 )#line:110
            O0000O0O00OOO0000 ._results [OOO0O000OOO0OO00O ]=OO0OO00O00O0O0O00 #line:111
            if OO0OO00O00O0O0O00 is not None :#line:112
                O0000O0O00OOO0000 ._results [SimpleCamRacer ._RIGHT ]=OO0OO00O00O0O0O00 #line:113
        else :#line:114
            O0000O0O00OOO0000 ._results [OOO0O000OOO0OO00O ]=O0000O0O00OOO0000 ._find_blob (OO00OO0O0OOO0O00O ,OOOOO0O0OO000OO0O ,O0OO0OOOOOOOO000O ,O0O0O000O0O0O000O ,0 ,OO0O0O00O00O0OO00 ,0 ,OOO0OOOOO0000OO00 )#line:115
    def detect (OO0OOOOOOOO0OOO0O ,OOO00O0OOO0OO000O ):#line:117
        OO0OOOOOOOO0OOO0O ._clear ()#line:118
        if OOO00O0OOO0OO000O is not None :#line:119
            OO0OO0OOO000OO000 =OOO00O0OOO0OO000O .shape [1 ]#line:120
            OOO000O0000O00OO0 =OOO00O0OOO0OO000O .shape [0 ]#line:121
            OO0O0O0OOOO00OOO0 =OO0OO0OOO000OO000 //2 #line:122
            O0OO0OO00OO0O00O0 =OOO000O0000O00OO0 -OO0OOOOOOOO0OOO0O ._lane_window_height #line:123
            OO0OOOOOOOO0OOO0O ._find_color (OOO00O0OOO0OO000O ,SimpleCamRacer ._RED ,OO0OO0OOO000OO000 ,OOO000O0000O00OO0 ,OO0O0O0OOOO00OOO0 ,O0OO0OO00OO0O00O0 )#line:125
            OO0OOOOOOOO0OOO0O ._find_color (OOO00O0OOO0OO000O ,SimpleCamRacer ._GREEN ,OO0OO0OOO000OO000 ,OOO000O0000O00OO0 ,OO0O0O0OOOO00OOO0 ,O0OO0OO00OO0O00O0 )#line:126
            OO0OOOOOOOO0OOO0O ._find_color (OOO00O0OOO0OO000O ,SimpleCamRacer ._BLUE ,OO0OO0OOO000OO000 ,OOO000O0000O00OO0 ,OO0O0O0OOOO00OOO0 ,O0OO0OO00OO0O00O0 )#line:127
            O0OO0000O0OOOO0OO =OO0OOOOOOOO0OOO0O ._results [SimpleCamRacer ._LEFT ]#line:129
            O0O0OOOOOOO0000OO =OO0OOOOOOOO0OOO0O ._results [SimpleCamRacer ._RIGHT ]#line:130
            OO00OOOO0OO00O00O =abs (OO0O0O0OOOO00OOO0 -O0OO0000O0OOOO0OO ['xy'][0 ])if O0OO0000O0OOOO0OO is not None else OO0O0O0OOOO00OOO0 #line:131
            O00O0OO0OO00O0O00 =abs (O0O0OOOOOOO0000OO ['xy'][0 ]-OO0O0O0OOOO00OOO0 )if O0O0OOOOOOO0000OO is not None else OO0OO0OOO000OO000 -OO0O0O0OOOO00OOO0 #line:132
            O000OOO0OOO0OOO00 =O00O0OO0OO00O0O00 -OO00OOOO0OO00O00O #line:134
            OO0OOOOOOOO0OOO0O ._left_velocity =OO0OOOOOOOO0OOO0O ._direction *OO0OOOOOOOO0OOO0O ._speed +OO0OOOOOOOO0OOO0O ._gain *O000OOO0OOO0OOO00 #line:135
            OO0OOOOOOOO0OOO0O ._right_velocity =OO0OOOOOOOO0OOO0O ._direction *OO0OOOOOOOO0OOO0O ._speed -OO0OOOOOOOO0OOO0O ._gain *O000OOO0OOO0OOO00 #line:136
            return True #line:137
        return False #line:138
    def _draw (OOO000O00O0OO000O ,OOOO000OOO00O0OO0 ,OO0O00O0OOO00O0O0 ,OO00OOOO0OO0OO000 ):#line:140
        if OO0O00O0OOO00O0O0 is not None :#line:141
            OOO0O0OOOO0OOO0OO ,O0OOOO0O00O00OOOO ,OO0O0OOO0OOOOOOOO ,O0OOOO00OOO00000O =OO0O00O0OOO00O0O0 ['box']#line:142
            cv2 .rectangle (OOOO000OOO00O0OO0 ,(OOO0O0OOOO0OOO0OO ,O0OOOO0O00O00OOOO ),(OO0O0OOO0OOOOOOOO ,O0OOOO00OOO00000O ),OO00OOOO0OO0OO000 ,3 )#line:143
            O000000O00O00O00O ,OOO00O0OOOO0O00OO =OO0O00O0OOO00O0O0 ['xy']#line:144
            cv2 .putText (OOOO000OOO00O0OO0 ,'x: {}px'.format (O000000O00O00O00O ),(OOO0O0OOOO0OOO0OO ,O0OOOO0O00O00OOOO -40 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:145
            cv2 .putText (OOOO000OOO00O0OO0 ,'y: {}px'.format (OOO00O0OOOO0O00OO ),(OOO0O0OOOO0OOO0OO ,O0OOOO0O00O00OOOO -25 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:146
            cv2 .putText (OOOO000OOO00O0OO0 ,'pixel: {}'.format (OO0O00O0OOO00O0O0 ['pixels']),(OOO0O0OOOO0OOO0OO ,O0OOOO0O00O00OOOO -10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:147
    def _draw_color (O0O00O0OO0OO0O00O ,O0O0000OO0OO0OOOO ,OO0O0OO000O00OO00 ,OO0O0OO0OO000OO0O ):#line:149
        if O0O00O0OO0OO0O00O ._left_lane_color ==OO0O0OO000O00OO00 or O0O00O0OO0OO0O00O ._right_lane_color ==OO0O0OO000O00OO00 :#line:150
            if O0O00O0OO0OO0O00O ._left_lane_color ==OO0O0OO000O00OO00 :#line:151
                O0O00O0OO0OO0O00O ._draw (O0O0000OO0OO0OOOO ,O0O00O0OO0OO0O00O ._results [SimpleCamRacer ._LEFT ],OO0O0OO0OO000OO0O )#line:152
            if O0O00O0OO0OO0O00O ._right_lane_color ==OO0O0OO000O00OO00 :#line:153
                O0O00O0OO0OO0O00O ._draw (O0O0000OO0OO0OOOO ,O0O00O0OO0OO0O00O ._results [SimpleCamRacer ._RIGHT ],OO0O0OO0OO000OO0O )#line:154
        else :#line:155
            O0O00O0OO0OO0O00O ._draw (O0O0000OO0OO0OOOO ,O0O00O0OO0OO0O00O ._results [OO0O0OO000O00OO00 ],OO0O0OO0OO000OO0O )#line:156
    def draw_result (O0O000O00000O0O0O ,O00OO00O0000O0OO0 ,clone =False ):#line:158
        if O00OO00O0000O0OO0 is not None :#line:159
            if clone :#line:160
                O00OO00O0000O0OO0 =O00OO00O0000O0OO0 .copy ()#line:161
            O0O000O00000O0O0O ._draw_color (O00OO00O0000O0OO0 ,SimpleCamRacer ._RED ,(0 ,0 ,255 ))#line:162
            O0O000O00000O0O0O ._draw_color (O00OO00O0000O0OO0 ,SimpleCamRacer ._GREEN ,(0 ,255 ,0 ))#line:163
            O0O000O00000O0O0O ._draw_color (O00OO00O0000O0OO0 ,SimpleCamRacer ._BLUE ,(255 ,0 ,0 ))#line:164
        return O00OO00O0000O0OO0 #line:165
    def set_lane_colors (O00O0OO0OOOOOOO0O ,O0000000OO0OOOOOO ,OOOOOOOOO000O000O ):#line:167
        if isinstance (O0000000OO0OOOOOO ,str ):#line:168
            O0000000OO0OOOOOO =O0000000OO0OOOOOO .lower ()#line:169
            if O0000000OO0OOOOOO in SimpleCamRacer ._COLORS :#line:170
                O00O0OO0OOOOOOO0O ._left_lane_color =SimpleCamRacer ._COLORS [O0000000OO0OOOOOO ]#line:171
        if isinstance (OOOOOOOOO000O000O ,str ):#line:172
            OOOOOOOOO000O000O =OOOOOOOOO000O000O .lower ()#line:173
            if OOOOOOOOO000O000O in SimpleCamRacer ._COLORS :#line:174
                O00O0OO0OOOOOOO0O ._right_lane_color =SimpleCamRacer ._COLORS [OOOOOOOOO000O000O ]#line:175
    def set_backward (OO000O0O0000O0000 ,backward =True ):#line:177
        OO000O0O0000O0000 ._direction =-1 if backward else 1 #line:178
    def set_speed (OO0O0O00O00O0OOOO ,O00OOO000OOO0OOOO ):#line:180
        if isinstance (O00OOO000OOO0OOOO ,(int ,float )):#line:181
            OO0O0O00O00O0OOOO ._speed =O00OOO000OOO0OOOO #line:182
    def set_gain (OOOOO00O0O0000O00 ,OOOOOOO0OOO0OOOOO ):#line:184
        if isinstance (OOOOOOO0OOO0OOOOO ,(int ,float )):#line:185
            OOOOO00O0O0000O00 ._gain =OOOOOOO0OOO0OOOOO #line:186
    def get_velocity (O0OOOO00OO0OO0000 ):#line:188
        return O0OOOO00OO0OO0000 ._left_velocity ,O0OOOO00OO0OO0000 ._right_velocity #line:189
    def get_left_velocity (O0OOOOOO0OO0000O0 ):#line:191
        return O0OOOOOO0OO0000O0 ._left_velocity #line:192
    def get_right_velocity (O0O000OOO00OO0OO0 ):#line:194
        return O0O000OOO00OO0OO0 ._right_velocity #line:195
    def get_xy (O0O00OOOOOOO00O00 ,O0OOOOO0O00O000O0 ):#line:197
        if isinstance (O0OOOOO0O00O000O0 ,str ):#line:198
            O0OOOOO0O00O000O0 =O0OOOOO0O00O000O0 .lower ()#line:199
            if O0OOOOO0O00O000O0 in SimpleCamRacer ._BLOBS :#line:200
                O0OOO0O0O0O0O00O0 =O0O00OOOOOOO00O00 ._results [SimpleCamRacer ._BLOBS [O0OOOOO0O00O000O0 ]]#line:201
                if O0OOO0O0O0O0O00O0 is not None :#line:202
                    return O0OOO0O0O0O0O00O0 ['xy']#line:203
        return -1 ,-1 #line:204
    def get_x (OO0OOO0OO0OO0OOO0 ,OOOO00OOO0OOOOOOO ):#line:206
        O0O0OO00OO0OO0OO0 ,_O00O00OOO0000OOO0 =OO0OOO0OO0OO0OOO0 .get_xy (OOOO00OOO0OOOOOOO )#line:207
        return O0O0OO00OO0OO0OO0 #line:208
    def get_y (O0O0OOOO00OOO0OO0 ,OOO000OO0OO0O0O00 ):#line:210
        _OO0OOO0OOO0O0O0OO ,O0O000OO0000O0OOO =O0O0OOOO00OOO0OO0 .get_xy (OOO000OO0OO0O0O00 )#line:211
        return O0O000OO0000O0OOO #line:212
    def get_box (O00O0OO0OO00000O0 ,OOO0000O0OO0O00O0 ):#line:214
        if isinstance (OOO0000O0OO0O00O0 ,str ):#line:215
            OOO0000O0OO0O00O0 =OOO0000O0OO0O00O0 .lower ()#line:216
            if OOO0000O0OO0O00O0 in SimpleCamRacer ._BLOBS :#line:217
                O00000O000OOOOO0O =O00O0OO0OO00000O0 ._results [SimpleCamRacer ._BLOBS [OOO0000O0OO0O00O0 ]]#line:218
                if O00000O000OOOOO0O is not None :#line:219
                    return O00000O000OOOOO0O ['box']#line:220
        return -1 ,-1 ,-1 ,-1 #line:221
    def get_width (OO0000OOOOOOO00O0 ,O00OO0OOO000O0O0O ):#line:223
        if isinstance (O00OO0OOO000O0O0O ,str ):#line:224
            O00OO0OOO000O0O0O =O00OO0OOO000O0O0O .lower ()#line:225
            if O00OO0OOO000O0O0O in SimpleCamRacer ._BLOBS :#line:226
                OO0OOO0OO0O0O0OO0 =OO0000OOOOOOO00O0 ._results [SimpleCamRacer ._BLOBS [O00OO0OOO000O0O0O ]]#line:227
                if OO0OOO0OO0O0O0OO0 is not None :#line:228
                    return OO0OOO0OO0O0O0OO0 ['width']#line:229
        return 0 #line:230
    def get_height (O00OOOO000000O000 ,OO0000O00OOO00OO0 ):#line:232
        if isinstance (OO0000O00OOO00OO0 ,str ):#line:233
            OO0000O00OOO00OO0 =OO0000O00OOO00OO0 .lower ()#line:234
            if OO0000O00OOO00OO0 in SimpleCamRacer ._BLOBS :#line:235
                O00OO0O0O0OOO00OO =O00OOOO000000O000 ._results [SimpleCamRacer ._BLOBS [OO0000O00OOO00OO0 ]]#line:236
                if O00OO0O0O0OOO00OO is not None :#line:237
                    return O00OO0O0O0OOO00OO ['height']#line:238
        return 0 #line:239
    def get_area (O00OO0OOO0O0000O0 ,OO0O00O000OO00000 ):#line:241
        if isinstance (OO0O00O000OO00000 ,str ):#line:242
            OO0O00O000OO00000 =OO0O00O000OO00000 .lower ()#line:243
            if OO0O00O000OO00000 in SimpleCamRacer ._BLOBS :#line:244
                OO0000O000OOOOOOO =O00OO0OOO0O0000O0 ._results [SimpleCamRacer ._BLOBS [OO0O00O000OO00000 ]]#line:245
                if OO0000O000OOOOOOO is not None :#line:246
                    return OO0000O000OOOOOOO ['area']#line:247
        return 0 #line:248
    def get_pixels (O0OO0000O0O0O000O ,O0OO0OO0OOO0O0000 ):#line:250
        if isinstance (O0OO0OO0OOO0O0000 ,str ):#line:251
            O0OO0OO0OOO0O0000 =O0OO0OO0OOO0O0000 .lower ()#line:252
            if O0OO0OO0OOO0O0000 in SimpleCamRacer ._BLOBS :#line:253
                OOOOOOOOOOOOO000O =O0OO0000O0O0O000O ._results [SimpleCamRacer ._BLOBS [O0OO0OO0OOO0O0000 ]]#line:254
                if OOOOOOOOOOOOO000O is not None :#line:255
                    return OOOOOOOOOOOOO000O ['pixels']#line:256
        return 0 #line:257
