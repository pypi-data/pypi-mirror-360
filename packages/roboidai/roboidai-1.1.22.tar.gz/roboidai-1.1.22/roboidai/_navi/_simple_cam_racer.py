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
    def __init__ (O0O000O0O0OOO0O00 ,red_h_range =(0 ,10 ,170 ,180 ),green_h_range =(40 ,80 ),blue_h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 ),lane_window_height =50 ):#line:25
        O0O000O0O0OOO0O00 ._h_range ={SimpleCamRacer ._RED :red_h_range ,SimpleCamRacer ._GREEN :green_h_range ,SimpleCamRacer ._BLUE :blue_h_range }#line:30
        O0O000O0O0OOO0O00 ._s_range =s_range #line:31
        O0O000O0O0OOO0O00 ._v_range =v_range #line:32
        O0O000O0O0OOO0O00 ._lane_window_height =lane_window_height #line:33
        O0O000O0O0OOO0O00 ._direction =1 #line:34
        O0O000O0O0OOO0O00 ._speed =50 #line:35
        O0O000O0O0OOO0O00 ._gain =0.1 #line:36
        O0O000O0O0OOO0O00 ._left_velocity =0 #line:37
        O0O000O0O0OOO0O00 ._right_velocity =0 #line:38
        O0O000O0O0OOO0O00 ._results ={}#line:39
        O0O000O0O0OOO0O00 ._clear ()#line:40
        O0O000O0O0OOO0O00 .set_lane_colors ('green','blue')#line:41
    def _clear (O00000OOO00OO0O00 ):#line:43
        O00000OOO00OO0O00 ._results [SimpleCamRacer ._LEFT ]=None #line:44
        O00000OOO00OO0O00 ._results [SimpleCamRacer ._RIGHT ]=None #line:45
        O00000OOO00OO0O00 ._results [SimpleCamRacer ._RED ]=None #line:46
        O00000OOO00OO0O00 ._results [SimpleCamRacer ._GREEN ]=None #line:47
        O00000OOO00OO0O00 ._results [SimpleCamRacer ._BLUE ]=None #line:48
    def _find_blob (O00OO000OOO00OO00 ,O00O000000OO0O0OO ,OOOO0O000OO0OO0OO ,O0OOO0OO00OOO0O00 ,OOOO0O00O0OOOO0OO ,OO0OO0000O0OOO0O0 ,O0O00O00O0O0O000O ,O0O0O0OOO0O0OOOOO ,OOOO0O00000OO000O ):#line:50
        O0OO00O0O0OO0O0O0 =O00O000000OO0O0OO [O0O0O0OOO0O0OOOOO :OOOO0O00000OO000O ,OO0OO0000O0OOO0O0 :O0O00O00O0O0O000O ]#line:51
        O0O00O0OOOOOOOO0O =cv2 .cvtColor (O0OO00O0O0OO0O0O0 ,cv2 .COLOR_BGR2HSV )#line:52
        OOOOO0OOO0O0OO00O =cv2 .inRange (O0O00O0OOOOOOOO0O ,(OOOO0O000OO0OO0OO [0 ],O0OOO0OO00OOO0O00 [0 ],OOOO0O00O0OOOO0OO [0 ]),(OOOO0O000OO0OO0OO [1 ],O0OOO0OO00OOO0O00 [1 ],OOOO0O00O0OOOO0OO [1 ]))#line:54
        if len (OOOO0O000OO0OO0OO )>=4 :#line:55
            OOOOO0OOO0O0OO00O |=cv2 .inRange (O0O00O0OOOOOOOO0O ,(OOOO0O000OO0OO0OO [2 ],O0OOO0OO00OOO0O00 [0 ],OOOO0O00O0OOOO0OO [0 ]),(OOOO0O000OO0OO0OO [3 ],O0OOO0OO00OOO0O00 [1 ],OOOO0O00O0OOOO0OO [1 ]))#line:56
        OO00000000OOO000O =np .ones ((3 ,3 ),np .uint8 )#line:58
        OOOOO0OOO0O0OO00O =cv2 .morphologyEx (OOOOO0OOO0O0OO00O ,cv2 .MORPH_OPEN ,OO00000000OOO000O )#line:59
        OOOOO0OOO0O0OO00O =cv2 .morphologyEx (OOOOO0OOO0O0OO00O ,cv2 .MORPH_CLOSE ,OO00000000OOO000O )#line:60
        O00O0OO00O0OO00O0 ,_O00O000O0OOO00O0O =cv2 .findContours (OOOOO0OOO0O0OO00O ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:62
        O0OO0OOOOO00OOO00 =[cv2 .contourArea (O00O0OO000000OO0O )for O00O0OO000000OO0O in O00O0OO00O0OO00O0 ]#line:63
        if O0OO0OOOOO00OOO00 :#line:64
            OO0OO0O0O000O0O00 =np .argmax (O0OO0OOOOO00OOO00 )#line:65
            OO00O0OOOO00O0O00 =int (O0OO0OOOOO00OOO00 [OO0OO0O0O000O0O00 ])#line:66
            if OO00O0OOOO00O0O00 >5 :#line:67
                O0O0OOO0O0OOO000O =O00O0OO00O0OO00O0 [OO0OO0O0O000O0O00 ]#line:68
                O0O000O00O0OOO000 ,O0000O0O00O00O000 ,OOOOO0O0000O0OOOO ,O0O0O0OO0OO000O00 =cv2 .boundingRect (O0O0OOO0O0OOO000O )#line:69
                OO000000O000OO000 ={'box':(O0O000O00O0OOO000 +OO0OO0000O0OOO0O0 ,O0000O0O00O00O000 +O0O0O0OOO0O0OOOOO ,O0O000O00O0OOO000 +OOOOO0O0000O0OOOO +OO0OO0000O0OOO0O0 ,O0000O0O00O00O000 +O0O0O0OO0OO000O00 +O0O0O0OOO0O0OOOOO ),'width':OOOOO0O0000O0OOOO ,'height':O0O0O0OO0OO000O00 ,'area':OOOOO0O0000O0OOOO *O0O0O0OO0OO000O00 ,'pixels':OO00O0OOOO00O0O00 }#line:76
                OOO00O000000O0O0O =cv2 .moments (O0O0OOO0O0OOO000O )#line:77
                O0OO0OO000OOOO000 =OOO00O000000O0O0O ['m00']#line:78
                if O0OO0OO000OOOO000 >0 :#line:79
                    OO000000O000OO000 ['xy']=(int (OOO00O000000O0O0O ['m10']/O0OO0OO000OOOO000 )+OO0OO0000O0OOO0O0 ,int (OOO00O000000O0O0O ['m01']/O0OO0OO000OOOO000 )+O0O0O0OOO0O0OOOOO )#line:80
                    return OO000000O000OO000 #line:81
        return None #line:82
    def _find_color (OOO0OOOOOO0O0OO00 ,O000OO00OO0O00OO0 ,O0OO00OOOO0000OOO ,OO0000O0000O0OO00 ,OO00000O0000O00O0 ,O000O000OOO0OO00O ,O0000O00O0O00OOO0 ):#line:84
        OOO00OO00000OOOOO =OOO0OOOOOO0O0OO00 ._h_range [O0OO00OOOO0000OOO ]#line:85
        O0O00O0OO0OO00O0O =OOO0OOOOOO0O0OO00 ._s_range #line:86
        OOOOO0O0OO00000OO =OOO0OOOOOO0O0OO00 ._v_range #line:87
        if OOO0OOOOOO0O0OO00 ._left_lane_color ==O0OO00OOOO0000OOO and OOO0OOOOOO0O0OO00 ._right_lane_color ==O0OO00OOOO0000OOO :#line:89
            O0OOOO00O000O0O00 =OOO0OOOOOO0O0OO00 ._find_blob (O000OO00OO0O00OO0 ,OOO00OO00000OOOOO ,O0O00O0OO0OO00O0O ,OOOOO0O0OO00000OO ,0 ,O000O000OOO0OO00O ,O0000O00O0O00OOO0 ,OO00000O0000O00O0 )#line:90
            O00O0OO00O00OOOOO =OOO0OOOOOO0O0OO00 ._find_blob (O000OO00OO0O00OO0 ,OOO00OO00000OOOOO ,O0O00O0OO0OO00O0O ,OOOOO0O0OO00000OO ,O000O000OOO0OO00O ,OO0000O0000O0OO00 ,O0000O00O0O00OOO0 ,OO00000O0000O00O0 )#line:91
            if O0OOOO00O000O0O00 is not None and O00O0OO00O00OOOOO is not None :#line:92
                OOO0OOOOOO0O0OO00 ._results [O0OO00OOOO0000OOO ]=O00O0OO00O00OOOOO if O00O0OO00O00OOOOO ['pixels']>O0OOOO00O000O0O00 ['pixels']else O0OOOO00O000O0O00 #line:93
                OOO0OOOOOO0O0OO00 ._results [SimpleCamRacer ._LEFT ]=O0OOOO00O000O0O00 #line:94
                OOO0OOOOOO0O0OO00 ._results [SimpleCamRacer ._RIGHT ]=O00O0OO00O00OOOOO #line:95
            elif O0OOOO00O000O0O00 is not None :#line:96
                OOO0OOOOOO0O0OO00 ._results [O0OO00OOOO0000OOO ]=O0OOOO00O000O0O00 #line:97
                OOO0OOOOOO0O0OO00 ._results [SimpleCamRacer ._LEFT ]=O0OOOO00O000O0O00 #line:98
            elif O00O0OO00O00OOOOO is not None :#line:99
                OOO0OOOOOO0O0OO00 ._results [O0OO00OOOO0000OOO ]=O00O0OO00O00OOOOO #line:100
                OOO0OOOOOO0O0OO00 ._results [SimpleCamRacer ._RIGHT ]=O00O0OO00O00OOOOO #line:101
            else :#line:102
                OOO0OOOOOO0O0OO00 ._results [O0OO00OOOO0000OOO ]=None #line:103
        elif OOO0OOOOOO0O0OO00 ._left_lane_color ==O0OO00OOOO0000OOO :#line:104
            OO00O000000OO0O00 =OOO0OOOOOO0O0OO00 ._find_blob (O000OO00OO0O00OO0 ,OOO00OO00000OOOOO ,O0O00O0OO0OO00O0O ,OOOOO0O0OO00000OO ,0 ,OO0000O0000O0OO00 ,O0000O00O0O00OOO0 ,OO00000O0000O00O0 )#line:105
            OOO0OOOOOO0O0OO00 ._results [O0OO00OOOO0000OOO ]=OO00O000000OO0O00 #line:106
            if OO00O000000OO0O00 is not None :#line:107
                OOO0OOOOOO0O0OO00 ._results [SimpleCamRacer ._LEFT ]=OO00O000000OO0O00 #line:108
        elif OOO0OOOOOO0O0OO00 ._right_lane_color ==O0OO00OOOO0000OOO :#line:109
            OO00O000000OO0O00 =OOO0OOOOOO0O0OO00 ._find_blob (O000OO00OO0O00OO0 ,OOO00OO00000OOOOO ,O0O00O0OO0OO00O0O ,OOOOO0O0OO00000OO ,0 ,OO0000O0000O0OO00 ,O0000O00O0O00OOO0 ,OO00000O0000O00O0 )#line:110
            OOO0OOOOOO0O0OO00 ._results [O0OO00OOOO0000OOO ]=OO00O000000OO0O00 #line:111
            if OO00O000000OO0O00 is not None :#line:112
                OOO0OOOOOO0O0OO00 ._results [SimpleCamRacer ._RIGHT ]=OO00O000000OO0O00 #line:113
        else :#line:114
            OOO0OOOOOO0O0OO00 ._results [O0OO00OOOO0000OOO ]=OOO0OOOOOO0O0OO00 ._find_blob (O000OO00OO0O00OO0 ,OOO00OO00000OOOOO ,O0O00O0OO0OO00O0O ,OOOOO0O0OO00000OO ,0 ,OO0000O0000O0OO00 ,0 ,OO00000O0000O00O0 )#line:115
    def detect (O0O0OO00000OOOO00 ,OOOOOO00O00OOOOO0 ):#line:117
        O0O0OO00000OOOO00 ._clear ()#line:118
        if OOOOOO00O00OOOOO0 is not None :#line:119
            OO00OOO00O0O0OOOO =OOOOOO00O00OOOOO0 .shape [1 ]#line:120
            OO0O00O0O00OOO000 =OOOOOO00O00OOOOO0 .shape [0 ]#line:121
            OO00OOO00OO0000OO =OO00OOO00O0O0OOOO //2 #line:122
            O0OO00OO00OO00OO0 =OO0O00O0O00OOO000 -O0O0OO00000OOOO00 ._lane_window_height #line:123
            O0O0OO00000OOOO00 ._find_color (OOOOOO00O00OOOOO0 ,SimpleCamRacer ._RED ,OO00OOO00O0O0OOOO ,OO0O00O0O00OOO000 ,OO00OOO00OO0000OO ,O0OO00OO00OO00OO0 )#line:125
            O0O0OO00000OOOO00 ._find_color (OOOOOO00O00OOOOO0 ,SimpleCamRacer ._GREEN ,OO00OOO00O0O0OOOO ,OO0O00O0O00OOO000 ,OO00OOO00OO0000OO ,O0OO00OO00OO00OO0 )#line:126
            O0O0OO00000OOOO00 ._find_color (OOOOOO00O00OOOOO0 ,SimpleCamRacer ._BLUE ,OO00OOO00O0O0OOOO ,OO0O00O0O00OOO000 ,OO00OOO00OO0000OO ,O0OO00OO00OO00OO0 )#line:127
            O0OOOOO00O0OOO0OO =O0O0OO00000OOOO00 ._results [SimpleCamRacer ._LEFT ]#line:129
            O00OO00O000O0OOO0 =O0O0OO00000OOOO00 ._results [SimpleCamRacer ._RIGHT ]#line:130
            OO0000OOO000OO000 =abs (OO00OOO00OO0000OO -O0OOOOO00O0OOO0OO ['xy'][0 ])if O0OOOOO00O0OOO0OO is not None else OO00OOO00OO0000OO #line:131
            O00000OO000O0OO0O =abs (O00OO00O000O0OOO0 ['xy'][0 ]-OO00OOO00OO0000OO )if O00OO00O000O0OOO0 is not None else OO00OOO00O0O0OOOO -OO00OOO00OO0000OO #line:132
            O000O00O00O0000OO =O00000OO000O0OO0O -OO0000OOO000OO000 #line:134
            O0O0OO00000OOOO00 ._left_velocity =O0O0OO00000OOOO00 ._direction *O0O0OO00000OOOO00 ._speed +O0O0OO00000OOOO00 ._gain *O000O00O00O0000OO #line:135
            O0O0OO00000OOOO00 ._right_velocity =O0O0OO00000OOOO00 ._direction *O0O0OO00000OOOO00 ._speed -O0O0OO00000OOOO00 ._gain *O000O00O00O0000OO #line:136
            return True #line:137
        return False #line:138
    def _draw (OO00OOO0OO0OO0OO0 ,O0OO0OOO000OO0O00 ,OO0000O000O0OOO0O ,O0OO0OOOO000000O0 ):#line:140
        if OO0000O000O0OOO0O is not None :#line:141
            O0OOO00O0OOOO00O0 ,OO000OOOO0OO0O000 ,O000O0O0O0OOOO0O0 ,OOOOOOOOOO0000OO0 =OO0000O000O0OOO0O ['box']#line:142
            cv2 .rectangle (O0OO0OOO000OO0O00 ,(O0OOO00O0OOOO00O0 ,OO000OOOO0OO0O000 ),(O000O0O0O0OOOO0O0 ,OOOOOOOOOO0000OO0 ),O0OO0OOOO000000O0 ,3 )#line:143
            OO000O00OO0O00000 ,O00000OO0OO0OOO00 =OO0000O000O0OOO0O ['xy']#line:144
            cv2 .putText (O0OO0OOO000OO0O00 ,'x: {}px'.format (OO000O00OO0O00000 ),(O0OOO00O0OOOO00O0 ,OO000OOOO0OO0O000 -40 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:145
            cv2 .putText (O0OO0OOO000OO0O00 ,'y: {}px'.format (O00000OO0OO0OOO00 ),(O0OOO00O0OOOO00O0 ,OO000OOOO0OO0O000 -25 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:146
            cv2 .putText (O0OO0OOO000OO0O00 ,'pixel: {}'.format (OO0000O000O0OOO0O ['pixels']),(O0OOO00O0OOOO00O0 ,OO000OOOO0OO0O000 -10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:147
    def _draw_color (OO00OO0O00O000O00 ,OOOOOO0O0OO0O00OO ,O0OO0OO0O00OO0OO0 ,O00OOO00OO000OOO0 ):#line:149
        if OO00OO0O00O000O00 ._left_lane_color ==O0OO0OO0O00OO0OO0 or OO00OO0O00O000O00 ._right_lane_color ==O0OO0OO0O00OO0OO0 :#line:150
            if OO00OO0O00O000O00 ._left_lane_color ==O0OO0OO0O00OO0OO0 :#line:151
                OO00OO0O00O000O00 ._draw (OOOOOO0O0OO0O00OO ,OO00OO0O00O000O00 ._results [SimpleCamRacer ._LEFT ],O00OOO00OO000OOO0 )#line:152
            if OO00OO0O00O000O00 ._right_lane_color ==O0OO0OO0O00OO0OO0 :#line:153
                OO00OO0O00O000O00 ._draw (OOOOOO0O0OO0O00OO ,OO00OO0O00O000O00 ._results [SimpleCamRacer ._RIGHT ],O00OOO00OO000OOO0 )#line:154
        else :#line:155
            OO00OO0O00O000O00 ._draw (OOOOOO0O0OO0O00OO ,OO00OO0O00O000O00 ._results [O0OO0OO0O00OO0OO0 ],O00OOO00OO000OOO0 )#line:156
    def draw_result (OOO0OO0O0OOO0OOOO ,O0OO0O00OOO00OOOO ,clone =False ):#line:158
        if O0OO0O00OOO00OOOO is not None :#line:159
            if clone :#line:160
                O0OO0O00OOO00OOOO =O0OO0O00OOO00OOOO .copy ()#line:161
            OOO0OO0O0OOO0OOOO ._draw_color (O0OO0O00OOO00OOOO ,SimpleCamRacer ._RED ,(0 ,0 ,255 ))#line:162
            OOO0OO0O0OOO0OOOO ._draw_color (O0OO0O00OOO00OOOO ,SimpleCamRacer ._GREEN ,(0 ,255 ,0 ))#line:163
            OOO0OO0O0OOO0OOOO ._draw_color (O0OO0O00OOO00OOOO ,SimpleCamRacer ._BLUE ,(255 ,0 ,0 ))#line:164
        return O0OO0O00OOO00OOOO #line:165
    def set_lane_colors (O0OO000OO00000O0O ,OOO00OO0O0OO00OO0 ,OO000OO0O00OO00O0 ):#line:167
        if isinstance (OOO00OO0O0OO00OO0 ,str ):#line:168
            OOO00OO0O0OO00OO0 =OOO00OO0O0OO00OO0 .lower ()#line:169
            if OOO00OO0O0OO00OO0 in SimpleCamRacer ._COLORS :#line:170
                O0OO000OO00000O0O ._left_lane_color =SimpleCamRacer ._COLORS [OOO00OO0O0OO00OO0 ]#line:171
        if isinstance (OO000OO0O00OO00O0 ,str ):#line:172
            OO000OO0O00OO00O0 =OO000OO0O00OO00O0 .lower ()#line:173
            if OO000OO0O00OO00O0 in SimpleCamRacer ._COLORS :#line:174
                O0OO000OO00000O0O ._right_lane_color =SimpleCamRacer ._COLORS [OO000OO0O00OO00O0 ]#line:175
    def set_backward (O00OOO0000O0OOOO0 ,backward =True ):#line:177
        O00OOO0000O0OOOO0 ._direction =-1 if backward else 1 #line:178
    def set_speed (O00OO0O0O0000O0O0 ,O0000OOO0OO0O00O0 ):#line:180
        if isinstance (O0000OOO0OO0O00O0 ,(int ,float )):#line:181
            O00OO0O0O0000O0O0 ._speed =O0000OOO0OO0O00O0 #line:182
    def set_gain (OO0000O00OO0O0O0O ,OOOOO00000OO00OO0 ):#line:184
        if isinstance (OOOOO00000OO00OO0 ,(int ,float )):#line:185
            OO0000O00OO0O0O0O ._gain =OOOOO00000OO00OO0 #line:186
    def get_velocity (O0OO0OOOOO00O0O0O ):#line:188
        return O0OO0OOOOO00O0O0O ._left_velocity ,O0OO0OOOOO00O0O0O ._right_velocity #line:189
    def get_left_velocity (O0OO00OO0O0OOO0O0 ):#line:191
        return O0OO00OO0O0OOO0O0 ._left_velocity #line:192
    def get_right_velocity (OO00O0O0000000OO0 ):#line:194
        return OO00O0O0000000OO0 ._right_velocity #line:195
    def get_xy (O00OOOO000O000O00 ,OOOOO0OO0O0OO00OO ):#line:197
        if isinstance (OOOOO0OO0O0OO00OO ,str ):#line:198
            OOOOO0OO0O0OO00OO =OOOOO0OO0O0OO00OO .lower ()#line:199
            if OOOOO0OO0O0OO00OO in SimpleCamRacer ._BLOBS :#line:200
                OOO0O0O0O00000O0O =O00OOOO000O000O00 ._results [SimpleCamRacer ._BLOBS [OOOOO0OO0O0OO00OO ]]#line:201
                if OOO0O0O0O00000O0O is not None :#line:202
                    return OOO0O0O0O00000O0O ['xy']#line:203
        return -1 ,-1 #line:204
    def get_x (O00OO0O000OO0OOO0 ,O0O000OO00O00000O ):#line:206
        O0OO0OOOOOOOO00OO ,_O0O00OO0OOOOOOO0O =O00OO0O000OO0OOO0 .get_xy (O0O000OO00O00000O )#line:207
        return O0OO0OOOOOOOO00OO #line:208
    def get_y (OO0O0O00000000000 ,OOOO0O0OOOO00000O ):#line:210
        _OOO00O0O0O0O000O0 ,O0000O00OOOO0OO0O =OO0O0O00000000000 .get_xy (OOOO0O0OOOO00000O )#line:211
        return O0000O00OOOO0OO0O #line:212
    def get_box (O0OO000OOO0OO000O ,O00OOOO00000OOO0O ):#line:214
        if isinstance (O00OOOO00000OOO0O ,str ):#line:215
            O00OOOO00000OOO0O =O00OOOO00000OOO0O .lower ()#line:216
            if O00OOOO00000OOO0O in SimpleCamRacer ._BLOBS :#line:217
                O0OOO0O0OOO00O000 =O0OO000OOO0OO000O ._results [SimpleCamRacer ._BLOBS [O00OOOO00000OOO0O ]]#line:218
                if O0OOO0O0OOO00O000 is not None :#line:219
                    return O0OOO0O0OOO00O000 ['box']#line:220
        return -1 ,-1 ,-1 ,-1 #line:221
    def get_width (O0O0O000O00OOOOO0 ,OOOOO0O0OOOO0OO0O ):#line:223
        if isinstance (OOOOO0O0OOOO0OO0O ,str ):#line:224
            OOOOO0O0OOOO0OO0O =OOOOO0O0OOOO0OO0O .lower ()#line:225
            if OOOOO0O0OOOO0OO0O in SimpleCamRacer ._BLOBS :#line:226
                O00OO0000OOO0OOOO =O0O0O000O00OOOOO0 ._results [SimpleCamRacer ._BLOBS [OOOOO0O0OOOO0OO0O ]]#line:227
                if O00OO0000OOO0OOOO is not None :#line:228
                    return O00OO0000OOO0OOOO ['width']#line:229
        return 0 #line:230
    def get_height (O0O00OO0000O00OO0 ,O00O00OO0OOOO0000 ):#line:232
        if isinstance (O00O00OO0OOOO0000 ,str ):#line:233
            O00O00OO0OOOO0000 =O00O00OO0OOOO0000 .lower ()#line:234
            if O00O00OO0OOOO0000 in SimpleCamRacer ._BLOBS :#line:235
                O0O0000O000OOO0OO =O0O00OO0000O00OO0 ._results [SimpleCamRacer ._BLOBS [O00O00OO0OOOO0000 ]]#line:236
                if O0O0000O000OOO0OO is not None :#line:237
                    return O0O0000O000OOO0OO ['height']#line:238
        return 0 #line:239
    def get_area (O0OO0OO0000O00O00 ,OOO0000O000O00OO0 ):#line:241
        if isinstance (OOO0000O000O00OO0 ,str ):#line:242
            OOO0000O000O00OO0 =OOO0000O000O00OO0 .lower ()#line:243
            if OOO0000O000O00OO0 in SimpleCamRacer ._BLOBS :#line:244
                O000OO0OO0OO0O0O0 =O0OO0OO0000O00O00 ._results [SimpleCamRacer ._BLOBS [OOO0000O000O00OO0 ]]#line:245
                if O000OO0OO0OO0O0O0 is not None :#line:246
                    return O000OO0OO0OO0O0O0 ['area']#line:247
        return 0 #line:248
    def get_pixels (O00OOOOO0OO0OOOO0 ,O0000OO0OO00OOO0O ):#line:250
        if isinstance (O0000OO0OO00OOO0O ,str ):#line:251
            O0000OO0OO00OOO0O =O0000OO0OO00OOO0O .lower ()#line:252
            if O0000OO0OO00OOO0O in SimpleCamRacer ._BLOBS :#line:253
                O00OOO00O0OO00OO0 =O00OOOOO0OO0OOOO0 ._results [SimpleCamRacer ._BLOBS [O0000OO0OO00OOO0O ]]#line:254
                if O00OOO00O0OO00OO0 is not None :#line:255
                    return O00OOO00O0OO00OO0 ['pixels']#line:256
        return 0 #line:257
