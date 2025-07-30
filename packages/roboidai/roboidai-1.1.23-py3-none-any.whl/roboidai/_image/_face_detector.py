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
import mediapipe as mp #line:4
from ._util import Util #line:5
class FaceDetector :#line:8
    def __init__ (OOO0O0O00O00O00O0 ,threshold =0.5 ):#line:9
        OOO0O0O00O00O00O0 ._clear ()#line:10
        try :#line:11
            OOO0O0O00O00O00O0 ._model =mp .solutions .face_detection .FaceDetection (min_detection_confidence =threshold )#line:12
        except :#line:13
            OOO0O0O00O00O00O0 ._model =None #line:14
    def _clear (OO000OOO0000O00OO ):#line:16
        OO000OOO0000O00OO ._points ={'left eye':None ,'right eye':None ,'left ear':None ,'right ear':None ,'nose':None ,'mouth':None }#line:24
        OO000OOO0000O00OO ._box =None #line:25
        OO000OOO0000O00OO ._width =0 #line:26
        OO000OOO0000O00OO ._height =0 #line:27
        OO000OOO0000O00OO ._area =0 #line:28
        OO000OOO0000O00OO ._confidence =0 #line:29
        OO000OOO0000O00OO ._drawings =None #line:30
    def detect (O0O0O00OOO000O0OO ,OO0O00OOO00OO00O0 ,padding =0 ):#line:32
        if OO0O00OOO00OO00O0 is not None and O0O0O00OOO000O0OO ._model is not None :#line:33
            OO0O00OOO00OO00O0 =cv2 .cvtColor (OO0O00OOO00OO00O0 ,cv2 .COLOR_BGR2RGB )#line:34
            OO0O00OOO00OO00O0 .flags .writeable =False #line:35
            O00000O0O0OOO000O =O0O0O00OOO000O0OO ._model .process (OO0O00OOO00OO00O0 )#line:36
            if O00000O0O0OOO000O and O00000O0O0OOO000O .detections and len (O00000O0O0OOO000O .detections )>0 :#line:37
                OOOOO0O0O0OOOOOO0 =O00000O0O0OOO000O .detections [0 ]#line:38
                OOOO0OOO00O0000OO =OOOOO0O0O0OOOOOO0 .location_data #line:39
                if OOOO0OOO00O0000OO :#line:40
                    OOO0OO0000OO0OO00 =OOOO0OOO00O0000OO .relative_bounding_box #line:41
                    if OOO0OO0000OO0OO00 :#line:42
                        O0OO0OOOO00O00O00 =OO0O00OOO00OO00O0 .shape [1 ]#line:43
                        OOOOO0000OOOO0OOO =OO0O00OOO00OO00O0 .shape [0 ]#line:44
                        O0O0OO000O00000O0 =O0O0O00OOO000O0OO ._box #line:45
                        if O0O0OO000O00000O0 is None :O0O0OO000O00000O0 =np .zeros (4 )#line:46
                        O0O0OO000O00000O0 [0 ]=max (0 ,OOO0OO0000OO0OO00 .xmin *O0OO0OOOO00O00O00 -padding )#line:47
                        O0O0OO000O00000O0 [1 ]=max (0 ,OOO0OO0000OO0OO00 .ymin *OOOOO0000OOOO0OOO -padding )#line:48
                        O0O0OO000O00000O0 [2 ]=min ((OOO0OO0000OO0OO00 .xmin +OOO0OO0000OO0OO00 .width )*O0OO0OOOO00O00O00 +padding ,O0OO0OOOO00O00O00 -1 )#line:49
                        O0O0OO000O00000O0 [3 ]=min ((OOO0OO0000OO0OO00 .ymin +OOO0OO0000OO0OO00 .height )*OOOOO0000OOOO0OOO +padding ,OOOOO0000OOOO0OOO -1 )#line:50
                        O0O0OO000O00000O0 =O0O0OO000O00000O0 .astype (np .int32 )#line:51
                        O0O0O00OOO000O0OO ._box =O0O0OO000O00000O0 #line:52
                        O0O0O00OOO000O0OO ._width =abs (O0O0OO000O00000O0 [2 ]-O0O0OO000O00000O0 [0 ])#line:53
                        O0O0O00OOO000O0OO ._height =abs (O0O0OO000O00000O0 [3 ]-O0O0OO000O00000O0 [1 ])#line:54
                        O0O0O00OOO000O0OO ._area =O0O0O00OOO000O0OO ._width *O0O0O00OOO000O0OO ._height #line:55
                        OOO00000OOO0O0000 =[O0OO000000O00O0OO .x for O0OO000000O00O0OO in OOOO0OOO00O0000OO .relative_keypoints ]#line:56
                        OO00O0O0O000OO0O0 =[OOO00OOOOOOO0OOO0 .y for OOO00OOOOOOO0OOO0 in OOOO0OOO00O0000OO .relative_keypoints ]#line:57
                        O0OO0OO0O000O00O0 =np .transpose (np .stack ((OOO00000OOO0O0000 ,OO00O0O0O000OO0O0 )))*(O0OO0OOOO00O00O00 ,OOOOO0000OOOO0OOO )#line:58
                        O0OO0OO0O000O00O0 =O0OO0OO0O000O00O0 .astype (np .int32 )#line:59
                        O0OO0O0OOO0O00OOO =O0O0O00OOO000O0OO ._points #line:60
                        O0OO0O0OOO0O00OOO ['left eye']=O0OO0OO0O000O00O0 [0 ]#line:61
                        O0OO0O0OOO0O00OOO ['right eye']=O0OO0OO0O000O00O0 [1 ]#line:62
                        O0OO0O0OOO0O00OOO ['left ear']=O0OO0OO0O000O00O0 [4 ]#line:63
                        O0OO0O0OOO0O00OOO ['right ear']=O0OO0OO0O000O00O0 [5 ]#line:64
                        O0OO0O0OOO0O00OOO ['nose']=O0OO0OO0O000O00O0 [2 ]#line:65
                        O0OO0O0OOO0O00OOO ['mouth']=O0OO0OO0O000O00O0 [3 ]#line:66
                        O0O0O00OOO000O0OO ._confidence =OOOOO0O0O0OOOOOO0 .score [0 ]#line:67
                        O0O0O00OOO000O0OO ._drawings =np .concatenate ((O0O0OO000O00000O0 ,O0OO0OO0O000O00O0 .reshape (-1 )),axis =None )#line:68
                        return True #line:69
        O0O0O00OOO000O0OO ._clear ()#line:70
        return False #line:71
    def _draw (O00OOOOO0000O0O0O ,O0O00OO00OOOO0OOO ,O00O0OO0OOO000OO0 ,OOO0OOO000000O000 ,O0O0OO0OO0OO00O0O ):#line:73
        cv2 .rectangle (O0O00OO00OOOO0OOO ,(O00O0OO0OOO000OO0 [0 ],O00O0OO0OOO000OO0 [1 ]),(O00O0OO0OOO000OO0 [2 ],O00O0OO0OOO000OO0 [3 ]),OOO0OOO000000O000 ,O0O0OO0OO0OO00O0O )#line:74
        cv2 .circle (O0O00OO00OOOO0OOO ,(O00O0OO0OOO000OO0 [4 ],O00O0OO0OOO000OO0 [5 ]),O0O0OO0OO0OO00O0O ,OOO0OOO000000O000 ,-1 )#line:75
        cv2 .circle (O0O00OO00OOOO0OOO ,(O00O0OO0OOO000OO0 [6 ],O00O0OO0OOO000OO0 [7 ]),O0O0OO0OO0OO00O0O ,OOO0OOO000000O000 ,-1 )#line:76
        cv2 .circle (O0O00OO00OOOO0OOO ,(O00O0OO0OOO000OO0 [8 ],O00O0OO0OOO000OO0 [9 ]),O0O0OO0OO0OO00O0O ,OOO0OOO000000O000 ,-1 )#line:77
        cv2 .circle (O0O00OO00OOOO0OOO ,(O00O0OO0OOO000OO0 [10 ],O00O0OO0OOO000OO0 [11 ]),O0O0OO0OO0OO00O0O ,OOO0OOO000000O000 ,-1 )#line:78
        cv2 .circle (O0O00OO00OOOO0OOO ,(O00O0OO0OOO000OO0 [12 ],O00O0OO0OOO000OO0 [13 ]),O0O0OO0OO0OO00O0O ,OOO0OOO000000O000 ,-1 )#line:79
        cv2 .circle (O0O00OO00OOOO0OOO ,(O00O0OO0OOO000OO0 [14 ],O00O0OO0OOO000OO0 [15 ]),O0O0OO0OO0OO00O0O ,OOO0OOO000000O000 ,-1 )#line:80
    def draw_result (O0O0O000O0OO0OOOO ,O00O000000O00OO00 ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:82
        if O00O000000O00OO00 is not None :#line:83
            if clone :#line:84
                O00O000000O00OO00 =O00O000000O00OO00 .copy ()#line:85
            if O0O0O000O0OO0OOOO ._drawings is not None :#line:86
                O0O0O000O0OO0OOOO ._draw (O00O000000O00OO00 ,O0O0O000O0OO0OOOO ._drawings ,color ,thickness )#line:87
        return O00O000000O00OO00 #line:88
    def get_xy (OO00OO00OOOO0OOOO ,id ='all'):#line:90
        if isinstance (id ,str ):#line:91
            id =id .lower ()#line:92
            if id =='all':#line:93
                return OO00OO00OOOO0OOOO ._points #line:94
            elif id in OO00OO00OOOO0OOOO ._points :#line:95
                return OO00OO00OOOO0OOOO ._points [id ]#line:96
        return None #line:97
    def get_box (OOOOO0OOOOO0OOO00 ):#line:99
        return OOOOO0OOOOO0OOO00 ._box #line:100
    def get_width (OOO000O0OOOOOO000 ):#line:102
        return OOO000O0OOOOOO000 ._width #line:103
    def get_height (O0O0OO00O0OO00O0O ):#line:105
        return O0O0OO00O0OO00O0O ._height #line:106
    def get_area (O0O0O000O000O0OO0 ):#line:108
        return O0O0O000O000O0OO0 ._area #line:109
    def get_conf (O00O000O000OOOO0O ):#line:111
        return O00O000O000OOOO0O ._confidence #line:112
    def get_orientation (OOOO00O00000OO00O ,degree =False ):#line:114
        O0O0O000O0OOOOOOO =OOOO00O00000OO00O .get_xy ('left eye')#line:115
        O0O000O00OO00OO00 =OOOO00O00000OO00O .get_xy ('right eye')#line:116
        if degree :#line:117
            return Util .degree (O0O0O000O0OOOOOOO ,O0O000O00OO00OO00 )#line:118
        else :#line:119
            return Util .radian (O0O0O000O0OOOOOOO ,O0O000O00OO00OO00 )#line:120
    def crop (O0OO0OO00O000OOO0 ,O00O00000O000000O ,clone =False ):#line:122
        if O00O00000O000000O is None or O0OO0OO00O000OOO0 ._box is None :return None #line:123
        if clone :O00O00000O000000O =O00O00000O000000O .copy ()#line:124
        O000OOOOO000OO000 =O0OO0OO00O000OOO0 ._box #line:125
        return O00O00000O000000O [O000OOOOO000OO000 [1 ]:O000OOOOO000OO000 [3 ],O000OOOOO000OO000 [0 ]:O000OOOOO000OO000 [2 ]]#line:126
    @staticmethod #line:128
    def distance (O00000O0OO0OOO00O ,O00O00OO00O000OOO ):#line:129
        return Util .distance (O00000O0OO0OOO00O ,O00O00OO00O000OOO )#line:130
    @staticmethod #line:132
    def degree (OOO00OO0OO00OOOOO ,OOO0OO0O0OO0OO000 ):#line:133
        return Util .degree (OOO00OO0OO00OOOOO ,OOO0OO0O0OO0OO000 )#line:134
    @staticmethod #line:136
    def radian (OOO0O000OO0O00OO0 ,OOOO000OO0O0O00O0 ):#line:137
        return Util .radian (OOO0O000OO0O00OO0 ,OOOO000OO0O0O00O0 )#line:138
