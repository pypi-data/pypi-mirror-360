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
import math #line:4
class ArucoDetector :#line:7
    def __init__ (OO0O0OO00O0000O0O ):#line:8
        OOOOOO0OO0OO0O0O0 =cv2 .aruco .getPredefinedDictionary (cv2 .aruco .DICT_ARUCO_ORIGINAL )#line:9
        O0OO000O0OO0000O0 =cv2 .aruco .DetectorParameters ()#line:10
        OO0O0OO00O0000O0O ._detector =cv2 .aruco .ArucoDetector (OOOOOO0OO0OO0O0O0 ,O0OO000O0OO0000O0 )#line:11
        OO0O0OO00O0000O0O ._clear ()#line:12
    def _clear (O0OO0OO0OO00OOOO0 ):#line:14
        O0OO0OO0OO00OOOO0 ._ids =[]#line:15
        O0OO0OO0OO00OOOO0 ._boxes ={}#line:16
        O0OO0OO0OO00OOOO0 ._xys ={}#line:17
        O0OO0OO0OO00OOOO0 ._radians ={}#line:18
        O0OO0OO0OO00OOOO0 ._degrees ={}#line:19
        O0OO0OO0OO00OOOO0 ._widths ={}#line:20
        O0OO0OO0OO00OOOO0 ._heights ={}#line:21
        O0OO0OO0OO00OOOO0 ._areas ={}#line:22
        O0OO0OO0OO00OOOO0 ._pixels ={}#line:23
        O0OO0OO0OO00OOOO0 ._corners ={}#line:24
        O0OO0OO0OO00OOOO0 ._drawings =[]#line:25
    def detect (OO0OO0OO00O00O00O ,O0OOO0OOOOOOOO00O ,min_pixels =-1 ):#line:27
        OO0OO0OO00O00O00O ._clear ()#line:28
        if O0OOO0OOOOOOOO00O is not None :#line:29
            O0O00O00000OOOO0O ,OO00OO0OO000OOOOO ,O00O0O0OO00O0OO0O =OO0OO0OO00O00O00O ._detector .detectMarkers (O0OOO0OOOOOOOO00O )#line:30
            if OO00OO0OO000OOOOO is not None :#line:31
                for O00O0OO0OO000OO00 in range (len (OO00OO0OO000OOOOO )):#line:32
                    O0O0000O0O00OO0OO =OO00OO0OO000OOOOO [O00O0OO0OO000OO00 ][0 ]#line:33
                    OO00000O00O000OOO =O0O00O00000OOOO0O [O00O0OO0OO000OO00 ][0 ]#line:34
                    OOO0O00OO0O0OOOOO =[]#line:35
                    O0OO0OO0O00OO0OOO =0 #line:36
                    OOO00O0O000O00000 =OO00000O00O000OOO [-1 ]#line:37
                    for OO000OO000OOOO0OO in range (len (OO00000O00O000OOO )):#line:38
                        O0OOOO00O00OOOO0O =OO00000O00O000OOO [OO000OO000OOOO0OO ]#line:39
                        O0OO0OO0O00OO0OOO +=(OOO00O0O000O00000 [0 ]+O0OOOO00O00OOOO0O [0 ])*(O0OOOO00O00OOOO0O [1 ]-OOO00O0O000O00000 [1 ])#line:40
                        OOO00O0O000O00000 =O0OOOO00O00OOOO0O #line:41
                        OOO0O00OO0O0OOOOO .append ((int (O0OOOO00O00OOOO0O [0 ]),int (O0OOOO00O00OOOO0O [1 ])))#line:42
                    if min_pixels <0 or O0OO0OO0O00OO0OOO >min_pixels :#line:43
                        OOOOO00O0OO0O0O00 =int (np .min (OO00000O00O000OOO [:,0 ]))#line:44
                        OO0OO0O0OO00O000O =int (np .max (OO00000O00O000OOO [:,0 ]))#line:45
                        O00O0OOOO0OO0O0OO =int (np .min (OO00000O00O000OOO [:,1 ]))#line:46
                        OOO000O00O00O0000 =int (np .max (OO00000O00O000OOO [:,1 ]))#line:47
                        OO0OO00OO0OO000OO =int (np .mean (OO00000O00O000OOO [:,0 ]))#line:48
                        O0O00O00O00OOOOO0 =int (np .mean (OO00000O00O000OOO [:,1 ]))#line:49
                        O0O0O0O0O000OOO00 =int ((OO00000O00O000OOO [0 ][0 ]+OO00000O00O000OOO [1 ][0 ])/2 )#line:50
                        OOO0OOO0000OOO000 =int ((OO00000O00O000OOO [0 ][1 ]+OO00000O00O000OOO [1 ][1 ])/2 )#line:51
                        O0OO00O0O00O0OO0O =abs (OO0OO0O0OO00O000O -OOOOO00O0OO0O0O00 );#line:52
                        OOOO00000OOOO0OO0 =abs (OOO000O00O00O0000 -O00O0OOOO0OO0O0OO );#line:53
                        O0O000O000O000O00 =math .atan2 (O0O00O00O00OOOOO0 -OOO0OOO0000OOO000 ,O0O0O0O0O000OOO00 -OO0OO00OO0OO000OO )#line:54
                        OO0OO0OO00O00O00O ._ids .append (O0O0000O0O00OO0OO )#line:55
                        OO0OO0OO00O00O00O ._boxes [O0O0000O0O00OO0OO ]=(OOOOO00O0OO0O0O00 ,O00O0OOOO0OO0O0OO ,OO0OO0O0OO00O000O ,OOO000O00O00O0000 )#line:56
                        OO0OO0OO00O00O00O ._xys [O0O0000O0O00OO0OO ]=(OO0OO00OO0OO000OO ,O0O00O00O00OOOOO0 )#line:57
                        OO0OO0OO00O00O00O ._radians [O0O0000O0O00OO0OO ]=O0O000O000O000O00 #line:58
                        OO0OO0OO00O00O00O ._degrees [O0O0000O0O00OO0OO ]=math .degrees (O0O000O000O000O00 )#line:59
                        OO0OO0OO00O00O00O ._widths [O0O0000O0O00OO0OO ]=O0OO00O0O00O0OO0O #line:60
                        OO0OO0OO00O00O00O ._heights [O0O0000O0O00OO0OO ]=OOOO00000OOOO0OO0 #line:61
                        OO0OO0OO00O00O00O ._areas [O0O0000O0O00OO0OO ]=O0OO00O0O00O0OO0O *OOOO00000OOOO0OO0 #line:62
                        OO0OO0OO00O00O00O ._pixels [O0O0000O0O00OO0OO ]=O0OO0OO0O00OO0OOO #line:63
                        OO0OO0OO00O00O00O ._corners [O0O0000O0O00OO0OO ]=OOO0O00OO0O0OOOOO #line:64
                        OO0OO0OO00O00O00O ._drawings .append ({'id':O0O0000O0O00OO0OO ,'corners':OOO0O00OO0O0OOOOO ,'center':(OO0OO00OO0OO000OO ,O0O00O00O00OOOOO0 ),'head':(O0O0O0O0O000OOO00 ,OOO0OOO0000OOO000 )})#line:70
                return len (OO0OO0OO00O00O00O ._ids )>0 #line:71
        return False #line:72
    def draw_result (O0O0O0O0O0OOOOOOO ,OOO000000OO0OOO0O ,clone =False ):#line:74
        if OOO000000OO0OOO0O is not None :#line:75
            if clone :#line:76
                OOO000000OO0OOO0O =OOO000000OO0OOO0O .copy ()#line:77
            O00000OO00OO0OOO0 =O0O0O0O0O0OOOOOOO ._drawings #line:78
            if O00000OO00OO0OOO0 is not None :#line:79
                for O0OO0OOOOOO0O0OOO in O00000OO00OO0OOO0 :#line:80
                    cv2 .putText (OOO000000OO0OOO0O ,str (O0OO0OOOOOO0O0OOO ['id']),O0OO0OOOOOO0O0OOO ['center'],cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,(0 ,165 ,255 ),2 )#line:83
                    OOOOOO00O00O0OO00 =O0OO0OOOOOO0O0OOO ['corners']#line:84
                    OOOO0O0OO00000000 =len (OOOOOO00O00O0OO00 )#line:85
                    for OO00O0OOO00O0OOO0 in range (OOOO0O0OO00000000 ):#line:86
                        cv2 .line (OOO000000OO0OOO0O ,OOOOOO00O00O0OO00 [OO00O0OOO00O0OOO0 ],OOOOOO00O00O0OO00 [(OO00O0OOO00O0OOO0 +1 )%OOOO0O0OO00000000 ],(0 ,165 ,255 ),3 )#line:87
                    cv2 .line (OOO000000OO0OOO0O ,O0OO0OOOOOO0O0OOO ['center'],O0OO0OOOOOO0O0OOO ['head'],(0 ,255 ,255 ),3 )#line:88
        return OOO000000OO0OOO0O #line:89
    def get_ids (OO000O0O0000O0O00 ):#line:91
        return OO000O0O0000O0O00 ._ids #line:92
    def _get (O0O000OOO000O0O00 ,OO000OO0OO0O00OOO ,id ='all'):#line:94
        if isinstance (id ,(int ,float )):#line:95
            id =int (id )#line:96
            if id in OO000OO0OO0O00OOO :#line:97
                return OO000OO0OO0O00OOO [id ]#line:98
        elif isinstance (id ,str ):#line:99
            id =id .lower ()#line:100
            if id =='all':#line:101
                return OO000OO0OO0O00OOO #line:102
        return None #line:103
    def get_box (O00O0OOOOO0OOOOOO ,id ='all'):#line:105
        return O00O0OOOOO0OOOOOO ._get (O00O0OOOOO0OOOOOO ._boxes ,id )#line:106
    def get_xy (O0000O0O0O000OO0O ,id ='all'):#line:108
        return O0000O0O0O000OO0O ._get (O0000O0O0O000OO0O ._xys ,id )#line:109
    def get_degree (O00O0OOOOO0O00OOO ,id ='all'):#line:111
        return O00O0OOOOO0O00OOO ._get (O00O0OOOOO0O00OOO ._degrees ,id )#line:112
    def get_radian (O0OOOO0O0O0OOO000 ,id ='all'):#line:114
        return O0OOOO0O0O0OOO000 ._get (O0OOOO0O0O0OOO000 ._radians ,id )#line:115
    def get_width (OOO0O00O000O0000O ,id ='all'):#line:117
        return OOO0O00O000O0000O ._get (OOO0O00O000O0000O ._widths ,id )#line:118
    def get_height (O000000OOO0O0O00O ,id ='all'):#line:120
        return O000000OOO0O0O00O ._get (O000000OOO0O0O00O ._heights ,id )#line:121
    def get_area (O0OOOOO0OOO00OOO0 ,id ='all'):#line:123
        return O0OOOOO0OOO00OOO0 ._get (O0OOOOO0OOO00OOO0 ._areas ,id )#line:124
    def get_pixels (OOO0O00OOOOOOOO00 ,id ='all'):#line:126
        return OOO0O00OOOOOOOO00 ._get (OOO0O00OOOOOOOO00 ._pixels ,id )#line:127
    def get_corners (O000O0O0OO0O0OO0O ,id ='all'):#line:129
        return O000O0O0OO0O0OO0O ._get (O000O0O0OO0O0OO0O ._corners ,id )#line:130
