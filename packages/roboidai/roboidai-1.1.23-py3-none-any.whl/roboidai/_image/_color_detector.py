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
    def __init__ (OO00O0OOOOOO0OOOO ,red_h_range =(0 ,10 ,170 ,180 ),green_h_range =(40 ,80 ),blue_h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 )):#line:7
        OO00O0OOOOOO0OOOO ._h_range ={'red':red_h_range ,'green':green_h_range ,'blue':blue_h_range }#line:12
        OO00O0OOOOOO0OOOO ._s_range =s_range #line:13
        OO00O0OOOOOO0OOOO ._v_range =v_range #line:14
        OO00O0OOOOOO0OOOO ._results ={}#line:15
        OO00O0OOOOOO0OOOO ._clear ()#line:16
    def _clear (OOOOO00OOOO00O0O0 ):#line:18
        OOOOO00OOOO00O0O0 ._results ['red']=None #line:19
        OOOOO00OOOO00O0O0 ._results ['green']=None #line:20
        OOOOO00OOOO00O0O0 ._results ['blue']=None #line:21
    def _find_blob (O00O000000OO000OO ,O0OO0000000O00000 ,OO0OO0O0O0O00O0OO ,OOOOO0OOOOO0O0O00 ,OO0OO00OOO0OO0O00 ):#line:23
        O0OO0O0000OO0000O =cv2 .cvtColor (O0OO0000000O00000 ,cv2 .COLOR_BGR2HSV )#line:24
        O0O0OOOOO00OOOO0O =cv2 .inRange (O0OO0O0000OO0000O ,(OO0OO0O0O0O00O0OO [0 ],OOOOO0OOOOO0O0O00 [0 ],OO0OO00OOO0OO0O00 [0 ]),(OO0OO0O0O0O00O0OO [1 ],OOOOO0OOOOO0O0O00 [1 ],OO0OO00OOO0OO0O00 [1 ]))#line:26
        if len (OO0OO0O0O0O00O0OO )>=4 :#line:27
            O0O0OOOOO00OOOO0O |=cv2 .inRange (O0OO0O0000OO0000O ,(OO0OO0O0O0O00O0OO [2 ],OOOOO0OOOOO0O0O00 [0 ],OO0OO00OOO0OO0O00 [0 ]),(OO0OO0O0O0O00O0OO [3 ],OOOOO0OOOOO0O0O00 [1 ],OO0OO00OOO0OO0O00 [1 ]))#line:28
        OOO00000O000O0O0O =np .ones ((3 ,3 ),np .uint8 )#line:30
        O0O0OOOOO00OOOO0O =cv2 .morphologyEx (O0O0OOOOO00OOOO0O ,cv2 .MORPH_OPEN ,OOO00000O000O0O0O )#line:31
        O0O0OOOOO00OOOO0O =cv2 .morphologyEx (O0O0OOOOO00OOOO0O ,cv2 .MORPH_CLOSE ,OOO00000O000O0O0O )#line:32
        O00OO00OOOOOO0O0O ,_OO0OO00OO0O0000O0 =cv2 .findContours (O0O0OOOOO00OOOO0O ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:34
        OO0OO00O0OOOO0O0O =[cv2 .contourArea (OOOO00OOO000O0O0O )for OOOO00OOO000O0O0O in O00OO00OOOOOO0O0O ]#line:35
        if OO0OO00O0OOOO0O0O :#line:36
            OO0OOO00O0O0OO0OO =np .argmax (OO0OO00O0OOOO0O0O )#line:37
            OOOO0O000O00OO00O =int (OO0OO00O0OOOO0O0O [OO0OOO00O0O0OO0OO ])#line:38
            if OOOO0O000O00OO00O >5 :#line:39
                O0OO000O00OO00OOO =O00OO00OOOOOO0O0O [OO0OOO00O0O0OO0OO ]#line:40
                OO0000O00OOO0O0OO ,O0O0O0OO00OO00O00 ,O00O000O000OO0OO0 ,OO0000OO0O00O0O0O =cv2 .boundingRect (O0OO000O00OO00OOO )#line:41
                OOO0OOO00OOOOOOOO ={'box':(OO0000O00OOO0O0OO ,O0O0O0OO00OO00O00 ,OO0000O00OOO0O0OO +O00O000O000OO0OO0 ,O0O0O0OO00OO00O00 +OO0000OO0O00O0O0O ),'width':O00O000O000OO0OO0 ,'height':OO0000OO0O00O0O0O ,'area':O00O000O000OO0OO0 *OO0000OO0O00O0O0O ,'pixels':OOOO0O000O00OO00O }#line:48
                O0OO0OOO0OO000000 =cv2 .moments (O0OO000O00OO00OOO )#line:49
                OOO00000O00000000 =O0OO0OOO0OO000000 ['m00']#line:50
                if OOO00000O00000000 >0 :#line:51
                    OOO0OOO00OOOOOOOO ['xy']=(int (O0OO0OOO0OO000000 ['m10']/OOO00000O00000000 ),int (O0OO0OOO0OO000000 ['m01']/OOO00000O00000000 ))#line:52
                    return OOO0OOO00OOOOOOOO #line:53
        return None #line:54
    def detect (O000O00O00OOO0000 ,OOO0OOO00O0OO00OO ):#line:56
        O000O00O00OOO0000 ._clear ()#line:57
        if OOO0OOO00O0OO00OO is not None :#line:58
            O0O00O0O00O0O0OOO =O000O00O00OOO0000 ._s_range #line:59
            O000OO000OO00OOOO =O000O00O00OOO0000 ._v_range #line:60
            O000O00O00OOO0000 ._results ['red']=O000O00O00OOO0000 ._find_blob (OOO0OOO00O0OO00OO ,O000O00O00OOO0000 ._h_range ['red'],O0O00O0O00O0O0OOO ,O000OO000OO00OOOO )#line:61
            O000O00O00OOO0000 ._results ['green']=O000O00O00OOO0000 ._find_blob (OOO0OOO00O0OO00OO ,O000O00O00OOO0000 ._h_range ['green'],O0O00O0O00O0O0OOO ,O000OO000OO00OOOO )#line:62
            O000O00O00OOO0000 ._results ['blue']=O000O00O00OOO0000 ._find_blob (OOO0OOO00O0OO00OO ,O000O00O00OOO0000 ._h_range ['blue'],O0O00O0O00O0O0OOO ,O000OO000OO00OOOO )#line:63
            return True #line:64
        return False #line:65
    def _draw (OO00O0OOOO0O0O0O0 ,OO00OO00OOOOO0O0O ,O0O0O00OOO0OO00OO ,O00OOOOO0OO00O00O ):#line:67
        if O0O0O00OOO0OO00OO is not None :#line:68
            O0O0O0OOOOOOOO0O0 ,O000O00OOOOO00O00 ,O00OO00O00O0000O0 ,OOO000O0O00O0OOOO =O0O0O00OOO0OO00OO ['box']#line:69
            cv2 .rectangle (OO00OO00OOOOO0O0O ,(O0O0O0OOOOOOOO0O0 ,O000O00OOOOO00O00 ),(O00OO00O00O0000O0 ,OOO000O0O00O0OOOO ),O00OOOOO0OO00O00O ,3 )#line:70
            OO00O0000OO0O0OOO ,O00OOOO0OOOO0000O =O0O0O00OOO0OO00OO ['xy']#line:71
            cv2 .putText (OO00OO00OOOOO0O0O ,'x: {}px'.format (OO00O0000OO0O0OOO ),(O0O0O0OOOOOOOO0O0 ,O000O00OOOOO00O00 -40 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:72
            cv2 .putText (OO00OO00OOOOO0O0O ,'y: {}px'.format (O00OOOO0OOOO0000O ),(O0O0O0OOOOOOOO0O0 ,O000O00OOOOO00O00 -25 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:73
            cv2 .putText (OO00OO00OOOOO0O0O ,'pixel: {}'.format (O0O0O00OOO0OO00OO ['pixels']),(O0O0O0OOOOOOOO0O0 ,O000O00OOOOO00O00 -10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(255 ,255 ,255 ),2 )#line:74
    def draw_result (OOOO0O00OO00OO0OO ,O00000OO0O0OO000O ,clone =False ):#line:76
        if O00000OO0O0OO000O is not None :#line:77
            if clone :#line:78
                O00000OO0O0OO000O =O00000OO0O0OO000O .copy ()#line:79
            OOOO0O00OO00OO0OO ._draw (O00000OO0O0OO000O ,OOOO0O00OO00OO0OO ._results ['red'],(0 ,0 ,255 ))#line:80
            OOOO0O00OO00OO0OO ._draw (O00000OO0O0OO000O ,OOOO0O00OO00OO0OO ._results ['green'],(0 ,255 ,0 ))#line:81
            OOOO0O00OO00OO0OO ._draw (O00000OO0O0OO000O ,OOOO0O00OO00OO0OO ._results ['blue'],(255 ,0 ,0 ))#line:82
        return O00000OO0O0OO000O #line:83
    def get_xy (O0O000000OOOOO00O ,O00OOO0OOO0OO0OO0 ):#line:85
        if isinstance (O00OOO0OOO0OO0OO0 ,str ):#line:86
            O00OOO0OOO0OO0OO0 =O00OOO0OOO0OO0OO0 .lower ()#line:87
            if O00OOO0OOO0OO0OO0 in O0O000000OOOOO00O ._results :#line:88
                O00OO00OO0OOO00O0 =O0O000000OOOOO00O ._results [O00OOO0OOO0OO0OO0 ]#line:89
                if O00OO00OO0OOO00O0 is not None :#line:90
                    return O00OO00OO0OOO00O0 ['xy']#line:91
        return -1 ,-1 #line:92
    def get_x (O0O0OO0O000OO000O ,OO00OOOO0000000OO ):#line:94
        O00OO000O0OO0O0OO ,_O00OO0O0OO0OO00O0 =O0O0OO0O000OO000O .get_xy (OO00OOOO0000000OO )#line:95
        return O00OO000O0OO0O0OO #line:96
    def get_y (O0000O0O0OOO0OO0O ,O0OOOOO0OOOOO00O0 ):#line:98
        _OO000OOOOO0O0OOO0 ,O000OO0O0OO00OOO0 =O0000O0O0OOO0OO0O .get_xy (O0OOOOO0OOOOO00O0 )#line:99
        return O000OO0O0OO00OOO0 #line:100
    def get_box (OOO0O00O000OOOO0O ,OO0000000OO00O0OO ):#line:102
        if isinstance (OO0000000OO00O0OO ,str ):#line:103
            OO0000000OO00O0OO =OO0000000OO00O0OO .lower ()#line:104
            if OO0000000OO00O0OO in OOO0O00O000OOOO0O ._results :#line:105
                O0O00OOOOO0O0000O =OOO0O00O000OOOO0O ._results [OO0000000OO00O0OO ]#line:106
                if O0O00OOOOO0O0000O is not None :#line:107
                    return O0O00OOOOO0O0000O ['box']#line:108
        return -1 ,-1 ,-1 ,-1 #line:109
    def get_width (O0O00O0O0O0OO000O ,OO0OOOOOO0O0OOO0O ):#line:111
        if isinstance (OO0OOOOOO0O0OOO0O ,str ):#line:112
            OO0OOOOOO0O0OOO0O =OO0OOOOOO0O0OOO0O .lower ()#line:113
            if OO0OOOOOO0O0OOO0O in O0O00O0O0O0OO000O ._results :#line:114
                O000OO0OOO0000O0O =O0O00O0O0O0OO000O ._results [OO0OOOOOO0O0OOO0O ]#line:115
                if O000OO0OOO0000O0O is not None :#line:116
                    return O000OO0OOO0000O0O ['width']#line:117
        return 0 #line:118
    def get_height (OOOOOO0O000OO0O00 ,O0OO000O0000O0O00 ):#line:120
        if isinstance (O0OO000O0000O0O00 ,str ):#line:121
            O0OO000O0000O0O00 =O0OO000O0000O0O00 .lower ()#line:122
            if O0OO000O0000O0O00 in OOOOOO0O000OO0O00 ._results :#line:123
                OO0OOO0O0O00O00OO =OOOOOO0O000OO0O00 ._results [O0OO000O0000O0O00 ]#line:124
                if OO0OOO0O0O00O00OO is not None :#line:125
                    return OO0OOO0O0O00O00OO ['height']#line:126
        return 0 #line:127
    def get_area (O00O0OOOO0O0OOO0O ,O0OO0O0O0O0O000O0 ):#line:129
        if isinstance (O0OO0O0O0O0O000O0 ,str ):#line:130
            O0OO0O0O0O0O000O0 =O0OO0O0O0O0O000O0 .lower ()#line:131
            if O0OO0O0O0O0O000O0 in O00O0OOOO0O0OOO0O ._results :#line:132
                O0O0OOO0O0O00OO0O =O00O0OOOO0O0OOO0O ._results [O0OO0O0O0O0O000O0 ]#line:133
                if O0O0OOO0O0O00OO0O is not None :#line:134
                    return O0O0OOO0O0O00OO0O ['area']#line:135
        return 0 #line:136
    def get_pixels (O00OO0O0OOOOO00OO ,O0OO0O0O00OO0O000 ):#line:138
        if isinstance (O0OO0O0O00OO0O000 ,str ):#line:139
            O0OO0O0O00OO0O000 =O0OO0O0O00OO0O000 .lower ()#line:140
            if O0OO0O0O00OO0O000 in O00OO0O0OOOOO00OO ._results :#line:141
                OOOO000OOO00O00O0 =O00OO0O0OOOOO00OO ._results [O0OO0O0O00OO0O000 ]#line:142
                if OOOO000OOO00O00O0 is not None :#line:143
                    return OOOO000OOO00O00O0 ['pixels']#line:144
        return 0 #line:145
    def wait_until (OO0OO0OOO0O00000O ,O0O0OO00O0O00O0O0 ,OO0O0OOOOOO0O0000 ,interval_msec =1 ,min_pixels =5 ,min_area =5 ):#line:147
        if not isinstance (OO0O0OOOOOO0O0000 ,(list ,tuple )):#line:148
            OO0O0OOOOOO0O0000 =(OO0O0OOOOOO0O0000 ,)#line:149
        O0O0O0O0000OO0OOO =None #line:150
        while O0O0O0O0000OO0OOO is None :#line:151
            OO0OO00O000O0OO00 =O0O0OO00O0O00O0O0 .read ()#line:152
            if OO0OO0OOO0O00000O .detect (OO0OO00O000O0OO00 ):#line:153
                O0O0O00000000OOOO =-1 #line:154
                for OOOOO000OOOOOOOO0 in OO0O0OOOOOO0O0000 :#line:155
                    O0OO00OOOO000O00O =OO0OO0OOO0O00000O .get_pixels (OOOOO000OOOOOOOO0 )#line:156
                    OOOO0OOOO0000O000 =OO0OO0OOO0O00000O .get_area (OOOOO000OOOOOOOO0 )#line:157
                    if O0OO00OOOO000O00O >min_pixels and OOOO0OOOO0000O000 >min_area and O0OO00OOOO000O00O >O0O0O00000000OOOO :#line:158
                        O0O0O00000000OOOO =O0OO00OOOO000O00O #line:159
                        O0O0O0O0000OO0OOO =OOOOO000OOOOOOOO0 #line:160
                OO0OO00O000O0OO00 =OO0OO0OOO0O00000O .draw_result (OO0OO00O000O0OO00 )#line:161
            O0O0OO00O0O00O0O0 .show (OO0OO00O000O0OO00 )#line:162
            if O0O0OO00O0O00O0O0 .check_key (interval_msec )=='esc':break #line:163
        return O0O0O0O0000OO0OOO #line:164
