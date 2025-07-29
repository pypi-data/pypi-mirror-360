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
class ColorDetector :#line:6
    def __init__ (OOO000OOO0O0OO0OO ,red_h_range =(0 ,10 ,170 ,180 ),green_h_range =(40 ,80 ),blue_h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 )):#line:7
        OOO000OOO0O0OO0OO ._h_range ={'red':red_h_range ,'green':green_h_range ,'blue':blue_h_range }#line:12
        OOO000OOO0O0OO0OO ._s_range =s_range #line:13
        OOO000OOO0O0OO0OO ._v_range =v_range #line:14
        OOO000OOO0O0OO0OO ._results ={}#line:15
        OOO000OOO0O0OO0OO ._clear ()#line:16
    def _clear (OO00O000000O00O00 ):#line:18
        OO00O000000O00O00 ._results ['red']=None #line:19
        OO00O000000O00O00 ._results ['green']=None #line:20
        OO00O000000O00O00 ._results ['blue']=None #line:21
    def _find_blob (OOO00OOO00000OOO0 ,OOOO0O0OOOOOOOO0O ,O0O0OO00O0OOOO000 ,OO0O000OO0O00O0OO ,OOOO0OOO000O000OO ):#line:23
        OO0O0O0OO0O0OOOOO =cv2 .cvtColor (OOOO0O0OOOOOOOO0O ,cv2 .COLOR_BGR2HSV )#line:24
        OOO0000O00O0O00O0 =cv2 .inRange (OO0O0O0OO0O0OOOOO ,(O0O0OO00O0OOOO000 [0 ],OO0O000OO0O00O0OO [0 ],OOOO0OOO000O000OO [0 ]),(O0O0OO00O0OOOO000 [1 ],OO0O000OO0O00O0OO [1 ],OOOO0OOO000O000OO [1 ]))#line:26
        if len (O0O0OO00O0OOOO000 )>=4 :#line:27
            OOO0000O00O0O00O0 |=cv2 .inRange (OO0O0O0OO0O0OOOOO ,(O0O0OO00O0OOOO000 [2 ],OO0O000OO0O00O0OO [0 ],OOOO0OOO000O000OO [0 ]),(O0O0OO00O0OOOO000 [3 ],OO0O000OO0O00O0OO [1 ],OOOO0OOO000O000OO [1 ]))#line:28
        OOO00OOO00OO0O00O =np .ones ((3 ,3 ),np .uint8 )#line:30
        OOO0000O00O0O00O0 =cv2 .morphologyEx (OOO0000O00O0O00O0 ,cv2 .MORPH_OPEN ,OOO00OOO00OO0O00O )#line:31
        OOO0000O00O0O00O0 =cv2 .morphologyEx (OOO0000O00O0O00O0 ,cv2 .MORPH_CLOSE ,OOO00OOO00OO0O00O )#line:32
        O00OO0OO00000OO0O ,_OOOOO00000O000000 =cv2 .findContours (OOO0000O00O0O00O0 ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:34
        O0OO0O00OO0O0OO0O =[cv2 .contourArea (OO0OO0OOOOOOOOOOO )for OO0OO0OOOOOOOOOOO in O00OO0OO00000OO0O ]#line:35
        if O0OO0O00OO0O0OO0O :#line:36
            OO0O00O00O0OO0O00 =np .argmax (O0OO0O00OO0O0OO0O )#line:37
            OOO0O0OOOOOOO0O0O =int (O0OO0O00OO0O0OO0O [OO0O00O00O0OO0O00 ])#line:38
            if OOO0O0OOOOOOO0O0O >5 :#line:39
                O0O0OOOOO000O00O0 =O00OO0OO00000OO0O [OO0O00O00O0OO0O00 ]#line:40
                OOO0OO0O0OOO000O0 ,O0O0O0OO0O00OO0OO ,OO0O00O0000000000 ,OO0OOO0000O0OOOOO =cv2 .boundingRect (O0O0OOOOO000O00O0 )#line:41
                O0O0OOOOOO0O00OO0 ={'box':(OOO0OO0O0OOO000O0 ,O0O0O0OO0O00OO0OO ,OOO0OO0O0OOO000O0 +OO0O00O0000000000 ,O0O0O0OO0O00OO0OO +OO0OOO0000O0OOOOO ),'width':OO0O00O0000000000 ,'height':OO0OOO0000O0OOOOO ,'area':OO0O00O0000000000 *OO0OOO0000O0OOOOO ,'pixels':OOO0O0OOOOOOO0O0O }#line:48
                OO000OO0O0O0OO0O0 =cv2 .moments (O0O0OOOOO000O00O0 )#line:49
                O0000OOO0OO0O0O00 =OO000OO0O0O0OO0O0 ['m00']#line:50
                if O0000OOO0OO0O0O00 >0 :#line:51
                    O0O0OOOOOO0O00OO0 ['xy']=(int (OO000OO0O0O0OO0O0 ['m10']/O0000OOO0OO0O0O00 ),int (OO000OO0O0O0OO0O0 ['m01']/O0000OOO0OO0O0O00 ))#line:52
                    return O0O0OOOOOO0O00OO0 #line:53
        return None #line:54
    def detect (O0O000OOO00O0000O ,OOO000O0000000000 ):#line:56
        O0O000OOO00O0000O ._clear ()#line:57
        if OOO000O0000000000 is not None :#line:58
            O00OOO000OOOO0OOO =O0O000OOO00O0000O ._s_range #line:59
            OO0O000000OO0000O =O0O000OOO00O0000O ._v_range #line:60
            O0O000OOO00O0000O ._results ['red']=O0O000OOO00O0000O ._find_blob (OOO000O0000000000 ,O0O000OOO00O0000O ._h_range ['red'],O00OOO000OOOO0OOO ,OO0O000000OO0000O )#line:61
            O0O000OOO00O0000O ._results ['green']=O0O000OOO00O0000O ._find_blob (OOO000O0000000000 ,O0O000OOO00O0000O ._h_range ['green'],O00OOO000OOOO0OOO ,OO0O000000OO0000O )#line:62
            O0O000OOO00O0000O ._results ['blue']=O0O000OOO00O0000O ._find_blob (OOO000O0000000000 ,O0O000OOO00O0000O ._h_range ['blue'],O00OOO000OOOO0OOO ,OO0O000000OO0000O )#line:63
            return True #line:64
        return False #line:65
    def _draw (OO0000O00O0OO000O ,OOO00OO00000O0OOO ,OO0OO0O0OO0OO0OOO ,OOO0000O0O00O00O0 ):#line:67
        if OO0OO0O0OO0OO0OOO is not None :#line:68
            O00O00OO0OOOO0O00 ,O0OOOOOO0O0OOOOOO ,O0OOOOO00OO0O0O00 ,O0OOO0OO00O0000O0 =OO0OO0O0OO0OO0OOO ['box']#line:69
            cv2 .rectangle (OOO00OO00000O0OOO ,(O00O00OO0OOOO0O00 ,O0OOOOOO0O0OOOOOO ),(O0OOOOO00OO0O0O00 ,O0OOO0OO00O0000O0 ),OOO0000O0O00O00O0 ,3 )#line:70
            O00O0O000OO0OO0O0 ,OOO000O0000000OO0 =OO0OO0O0OO0OO0OOO ['xy']#line:71
            cv2 .putText (OOO00OO00000O0OOO ,'x: {}px'.format (O00O0O000OO0OO0O0 ),(O00O00OO0OOOO0O00 ,O0OOOOOO0O0OOOOOO -40 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:72
            cv2 .putText (OOO00OO00000O0OOO ,'y: {}px'.format (OOO000O0000000OO0 ),(O00O00OO0OOOO0O00 ,O0OOOOOO0O0OOOOOO -25 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:73
            cv2 .putText (OOO00OO00000O0OOO ,'pixel: {}'.format (OO0OO0O0OO0OO0OOO ['pixels']),(O00O00OO0OOOO0O00 ,O0OOOOOO0O0OOOOOO -10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:74
    def draw_result (O00OOOO000OO000O0 ,OOO00OOO00OO0000O ,clone =False ):#line:76
        if OOO00OOO00OO0000O is not None :#line:77
            if clone :#line:78
                OOO00OOO00OO0000O =OOO00OOO00OO0000O .copy ()#line:79
            O00OOOO000OO000O0 ._draw (OOO00OOO00OO0000O ,O00OOOO000OO000O0 ._results ['red'],(0 ,0 ,255 ))#line:80
            O00OOOO000OO000O0 ._draw (OOO00OOO00OO0000O ,O00OOOO000OO000O0 ._results ['green'],(0 ,255 ,0 ))#line:81
            O00OOOO000OO000O0 ._draw (OOO00OOO00OO0000O ,O00OOOO000OO000O0 ._results ['blue'],(255 ,0 ,0 ))#line:82
        return OOO00OOO00OO0000O #line:83
    def get_xy (OO000O000000O000O ,OO0OOO0OOO00OOO0O ):#line:85
        if isinstance (OO0OOO0OOO00OOO0O ,str ):#line:86
            OO0OOO0OOO00OOO0O =OO0OOO0OOO00OOO0O .lower ()#line:87
            if OO0OOO0OOO00OOO0O in OO000O000000O000O ._results :#line:88
                O0OO0000O0000O0OO =OO000O000000O000O ._results [OO0OOO0OOO00OOO0O ]#line:89
                if O0OO0000O0000O0OO is not None :#line:90
                    return O0OO0000O0000O0OO ['xy']#line:91
        return -1 ,-1 #line:92
    def get_x (O00O0O000OOO00OO0 ,OOOO0O0O000O00OOO ):#line:94
        O0OOO0OO0OOO000OO ,_OO0O00O00OOO0OO00 =O00O0O000OOO00OO0 .get_xy (OOOO0O0O000O00OOO )#line:95
        return O0OOO0OO0OOO000OO #line:96
    def get_y (OOO00OO0OOO00O0OO ,OOOOOO0OO000OOO00 ):#line:98
        _O00O0O0OOO0OOOO00 ,OOO0OOO000OO000O0 =OOO00OO0OOO00O0OO .get_xy (OOOOOO0OO000OOO00 )#line:99
        return OOO0OOO000OO000O0 #line:100
    def get_box (OO0OO00OOO0O0O000 ,OO000000000O000OO ):#line:102
        if isinstance (OO000000000O000OO ,str ):#line:103
            OO000000000O000OO =OO000000000O000OO .lower ()#line:104
            if OO000000000O000OO in OO0OO00OOO0O0O000 ._results :#line:105
                O0O0OO000O00O0OO0 =OO0OO00OOO0O0O000 ._results [OO000000000O000OO ]#line:106
                if O0O0OO000O00O0OO0 is not None :#line:107
                    return O0O0OO000O00O0OO0 ['box']#line:108
        return -1 ,-1 ,-1 ,-1 #line:109
    def get_width (OOOOO0O000O0000O0 ,OOOO00O00O00000OO ):#line:111
        if isinstance (OOOO00O00O00000OO ,str ):#line:112
            OOOO00O00O00000OO =OOOO00O00O00000OO .lower ()#line:113
            if OOOO00O00O00000OO in OOOOO0O000O0000O0 ._results :#line:114
                OOOOO0O00OO0OOOO0 =OOOOO0O000O0000O0 ._results [OOOO00O00O00000OO ]#line:115
                if OOOOO0O00OO0OOOO0 is not None :#line:116
                    return OOOOO0O00OO0OOOO0 ['width']#line:117
        return 0 #line:118
    def get_height (O0O00O00OO0O00O0O ,OO00O0O000O0000OO ):#line:120
        if isinstance (OO00O0O000O0000OO ,str ):#line:121
            OO00O0O000O0000OO =OO00O0O000O0000OO .lower ()#line:122
            if OO00O0O000O0000OO in O0O00O00OO0O00O0O ._results :#line:123
                O0O0OO00OO0O00OOO =O0O00O00OO0O00O0O ._results [OO00O0O000O0000OO ]#line:124
                if O0O0OO00OO0O00OOO is not None :#line:125
                    return O0O0OO00OO0O00OOO ['height']#line:126
        return 0 #line:127
    def get_area (O0O0O0OO0000OOO00 ,OOOO0O0000OOOOO00 ):#line:129
        if isinstance (OOOO0O0000OOOOO00 ,str ):#line:130
            OOOO0O0000OOOOO00 =OOOO0O0000OOOOO00 .lower ()#line:131
            if OOOO0O0000OOOOO00 in O0O0O0OO0000OOO00 ._results :#line:132
                OO00000O00O0O0O00 =O0O0O0OO0000OOO00 ._results [OOOO0O0000OOOOO00 ]#line:133
                if OO00000O00O0O0O00 is not None :#line:134
                    return OO00000O00O0O0O00 ['area']#line:135
        return 0 #line:136
    def get_pixels (O0OO00O0OOO0OO0OO ,OOO0OOOO0O0O0O000 ):#line:138
        if isinstance (OOO0OOOO0O0O0O000 ,str ):#line:139
            OOO0OOOO0O0O0O000 =OOO0OOOO0O0O0O000 .lower ()#line:140
            if OOO0OOOO0O0O0O000 in O0OO00O0OOO0OO0OO ._results :#line:141
                OO0O0O00000OOOOO0 =O0OO00O0OOO0OO0OO ._results [OOO0OOOO0O0O0O000 ]#line:142
                if OO0O0O00000OOOOO0 is not None :#line:143
                    return OO0O0O00000OOOOO0 ['pixels']#line:144
        return 0 #line:145
    def wait_until (O0O00OO0O0O00OOO0 ,OOOO0O0OOO0OOO000 ,OOOOOO000O0O0OO00 ,interval_msec =1 ,min_pixels =5 ,min_area =5 ):#line:147
        if not isinstance (OOOOOO000O0O0OO00 ,(list ,tuple )):#line:148
            OOOOOO000O0O0OO00 =(OOOOOO000O0O0OO00 ,)#line:149
        OOO0O0O000OO0OOO0 =None #line:150
        while OOO0O0O000OO0OOO0 is None :#line:151
            OO0OO0O0OOO0O000O =OOOO0O0OOO0OOO000 .read ()#line:152
            if O0O00OO0O0O00OOO0 .detect (OO0OO0O0OOO0O000O ):#line:153
                OO00O0OO0O0OO0000 =-1 #line:154
                for OO0O0OO0O0O0OOO0O in OOOOOO000O0O0OO00 :#line:155
                    OOOOO0OOO00OO000O =O0O00OO0O0O00OOO0 .get_pixels (OO0O0OO0O0O0OOO0O )#line:156
                    OO00O00O000000O0O =O0O00OO0O0O00OOO0 .get_area (OO0O0OO0O0O0OOO0O )#line:157
                    if OOOOO0OOO00OO000O >min_pixels and OO00O00O000000O0O >min_area and OOOOO0OOO00OO000O >OO00O0OO0O0OO0000 :#line:158
                        OO00O0OO0O0OO0000 =OOOOO0OOO00OO000O #line:159
                        OOO0O0O000OO0OOO0 =OO0O0OO0O0O0OOO0O #line:160
                OO0OO0O0OOO0O000O =O0O00OO0O0O00OOO0 .draw_result (OO0OO0O0OOO0O000O )#line:161
            OOOO0O0OOO0OOO000 .show (OO0OO0O0OOO0O000O )#line:162
            if OOOO0O0OOO0OOO000 .check_key (interval_msec )=='esc':break #line:163
        return OOO0O0O000OO0OOO0 #line:164
