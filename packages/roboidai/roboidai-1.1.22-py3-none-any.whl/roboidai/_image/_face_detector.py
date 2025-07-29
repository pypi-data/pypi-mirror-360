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
    def __init__ (O0OO0OOO00OOO0O0O ,threshold =0.5 ):#line:9
        O0OO0OOO00OOO0O0O ._clear ()#line:10
        try :#line:11
            O0OO0OOO00OOO0O0O ._model =mp .solutions .face_detection .FaceDetection (min_detection_confidence =threshold )#line:12
        except :#line:13
            O0OO0OOO00OOO0O0O ._model =None #line:14
    def _clear (OOOO000O00O00O0OO ):#line:16
        OOOO000O00O00O0OO ._points ={'left eye':None ,'right eye':None ,'left ear':None ,'right ear':None ,'nose':None ,'mouth':None }#line:24
        OOOO000O00O00O0OO ._box =None #line:25
        OOOO000O00O00O0OO ._width =0 #line:26
        OOOO000O00O00O0OO ._height =0 #line:27
        OOOO000O00O00O0OO ._area =0 #line:28
        OOOO000O00O00O0OO ._confidence =0 #line:29
        OOOO000O00O00O0OO ._drawings =None #line:30
    def detect (OO0000O0OOO0O0O0O ,OOOOOO0O000O000O0 ,padding =0 ):#line:32
        if OOOOOO0O000O000O0 is not None and OO0000O0OOO0O0O0O ._model is not None :#line:33
            OOOOOO0O000O000O0 =cv2 .cvtColor (OOOOOO0O000O000O0 ,cv2 .COLOR_BGR2RGB )#line:34
            OOOOOO0O000O000O0 .flags .writeable =False #line:35
            O0000000000000O0O =OO0000O0OOO0O0O0O ._model .process (OOOOOO0O000O000O0 )#line:36
            if O0000000000000O0O and O0000000000000O0O .detections and len (O0000000000000O0O .detections )>0 :#line:37
                O0OOO0000O0OO0OO0 =O0000000000000O0O .detections [0 ]#line:38
                OOO0OO0000O0OO0OO =O0OOO0000O0OO0OO0 .location_data #line:39
                if OOO0OO0000O0OO0OO :#line:40
                    O0OO0OOO0OOO0000O =OOO0OO0000O0OO0OO .relative_bounding_box #line:41
                    if O0OO0OOO0OOO0000O :#line:42
                        O00OO00000O00OO0O =OOOOOO0O000O000O0 .shape [1 ]#line:43
                        OOO0OO000OO00O000 =OOOOOO0O000O000O0 .shape [0 ]#line:44
                        OO00O0O0O0OO0O0OO =OO0000O0OOO0O0O0O ._box #line:45
                        if OO00O0O0O0OO0O0OO is None :OO00O0O0O0OO0O0OO =np .zeros (4 )#line:46
                        OO00O0O0O0OO0O0OO [0 ]=max (0 ,O0OO0OOO0OOO0000O .xmin *O00OO00000O00OO0O -padding )#line:47
                        OO00O0O0O0OO0O0OO [1 ]=max (0 ,O0OO0OOO0OOO0000O .ymin *OOO0OO000OO00O000 -padding )#line:48
                        OO00O0O0O0OO0O0OO [2 ]=min ((O0OO0OOO0OOO0000O .xmin +O0OO0OOO0OOO0000O .width )*O00OO00000O00OO0O +padding ,O00OO00000O00OO0O -1 )#line:49
                        OO00O0O0O0OO0O0OO [3 ]=min ((O0OO0OOO0OOO0000O .ymin +O0OO0OOO0OOO0000O .height )*OOO0OO000OO00O000 +padding ,OOO0OO000OO00O000 -1 )#line:50
                        OO00O0O0O0OO0O0OO =OO00O0O0O0OO0O0OO .astype (np .int32 )#line:51
                        OO0000O0OOO0O0O0O ._box =OO00O0O0O0OO0O0OO #line:52
                        OO0000O0OOO0O0O0O ._width =abs (OO00O0O0O0OO0O0OO [2 ]-OO00O0O0O0OO0O0OO [0 ])#line:53
                        OO0000O0OOO0O0O0O ._height =abs (OO00O0O0O0OO0O0OO [3 ]-OO00O0O0O0OO0O0OO [1 ])#line:54
                        OO0000O0OOO0O0O0O ._area =OO0000O0OOO0O0O0O ._width *OO0000O0OOO0O0O0O ._height #line:55
                        O0000O0000000O0OO =[OO0000000OOOO0OO0 .x for OO0000000OOOO0OO0 in OOO0OO0000O0OO0OO .relative_keypoints ]#line:56
                        OOOO0OO00O0OO0OO0 =[O00OOOOO0OOOO0OOO .y for O00OOOOO0OOOO0OOO in OOO0OO0000O0OO0OO .relative_keypoints ]#line:57
                        O0OOOO0000OOO0O00 =np .transpose (np .stack ((O0000O0000000O0OO ,OOOO0OO00O0OO0OO0 )))*(O00OO00000O00OO0O ,OOO0OO000OO00O000 )#line:58
                        O0OOOO0000OOO0O00 =O0OOOO0000OOO0O00 .astype (np .int32 )#line:59
                        OOO0O0OO00OO0O0O0 =OO0000O0OOO0O0O0O ._points #line:60
                        OOO0O0OO00OO0O0O0 ['left eye']=O0OOOO0000OOO0O00 [0 ]#line:61
                        OOO0O0OO00OO0O0O0 ['right eye']=O0OOOO0000OOO0O00 [1 ]#line:62
                        OOO0O0OO00OO0O0O0 ['left ear']=O0OOOO0000OOO0O00 [4 ]#line:63
                        OOO0O0OO00OO0O0O0 ['right ear']=O0OOOO0000OOO0O00 [5 ]#line:64
                        OOO0O0OO00OO0O0O0 ['nose']=O0OOOO0000OOO0O00 [2 ]#line:65
                        OOO0O0OO00OO0O0O0 ['mouth']=O0OOOO0000OOO0O00 [3 ]#line:66
                        OO0000O0OOO0O0O0O ._confidence =O0OOO0000O0OO0OO0 .score [0 ]#line:67
                        OO0000O0OOO0O0O0O ._drawings =np .concatenate ((OO00O0O0O0OO0O0OO ,O0OOOO0000OOO0O00 .reshape (-1 )),axis =None )#line:68
                        return True #line:69
        OO0000O0OOO0O0O0O ._clear ()#line:70
        return False #line:71
    def _draw (OO00O00OO0O0000OO ,OO00000OO0OOOO000 ,OOO00O00000O0OO0O ,OOOOO0OO0OOO0000O ,O0OO0000OOO0O00O0 ):#line:73
        cv2 .rectangle (OO00000OO0OOOO000 ,(OOO00O00000O0OO0O [0 ],OOO00O00000O0OO0O [1 ]),(OOO00O00000O0OO0O [2 ],OOO00O00000O0OO0O [3 ]),OOOOO0OO0OOO0000O ,O0OO0000OOO0O00O0 )#line:74
        cv2 .circle (OO00000OO0OOOO000 ,(OOO00O00000O0OO0O [4 ],OOO00O00000O0OO0O [5 ]),O0OO0000OOO0O00O0 ,OOOOO0OO0OOO0000O ,-1 )#line:75
        cv2 .circle (OO00000OO0OOOO000 ,(OOO00O00000O0OO0O [6 ],OOO00O00000O0OO0O [7 ]),O0OO0000OOO0O00O0 ,OOOOO0OO0OOO0000O ,-1 )#line:76
        cv2 .circle (OO00000OO0OOOO000 ,(OOO00O00000O0OO0O [8 ],OOO00O00000O0OO0O [9 ]),O0OO0000OOO0O00O0 ,OOOOO0OO0OOO0000O ,-1 )#line:77
        cv2 .circle (OO00000OO0OOOO000 ,(OOO00O00000O0OO0O [10 ],OOO00O00000O0OO0O [11 ]),O0OO0000OOO0O00O0 ,OOOOO0OO0OOO0000O ,-1 )#line:78
        cv2 .circle (OO00000OO0OOOO000 ,(OOO00O00000O0OO0O [12 ],OOO00O00000O0OO0O [13 ]),O0OO0000OOO0O00O0 ,OOOOO0OO0OOO0000O ,-1 )#line:79
        cv2 .circle (OO00000OO0OOOO000 ,(OOO00O00000O0OO0O [14 ],OOO00O00000O0OO0O [15 ]),O0OO0000OOO0O00O0 ,OOOOO0OO0OOO0000O ,-1 )#line:80
    def draw_result (O00O000O0000O00OO ,O0O0O000O00000000 ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:82
        if O0O0O000O00000000 is not None :#line:83
            if clone :#line:84
                O0O0O000O00000000 =O0O0O000O00000000 .copy ()#line:85
            if O00O000O0000O00OO ._drawings is not None :#line:86
                O00O000O0000O00OO ._draw (O0O0O000O00000000 ,O00O000O0000O00OO ._drawings ,color ,thickness )#line:87
        return O0O0O000O00000000 #line:88
    def get_xy (OOO00OO0OOO0O0OOO ,id ='all'):#line:90
        if isinstance (id ,str ):#line:91
            id =id .lower ()#line:92
            if id =='all':#line:93
                return OOO00OO0OOO0O0OOO ._points #line:94
            elif id in OOO00OO0OOO0O0OOO ._points :#line:95
                return OOO00OO0OOO0O0OOO ._points [id ]#line:96
        return None #line:97
    def get_box (O0OOO0OO000OOO0O0 ):#line:99
        return O0OOO0OO000OOO0O0 ._box #line:100
    def get_width (OO000O0O00OOO00OO ):#line:102
        return OO000O0O00OOO00OO ._width #line:103
    def get_height (O00OOOO00000O0000 ):#line:105
        return O00OOOO00000O0000 ._height #line:106
    def get_area (O0OOO0O0O0000OOO0 ):#line:108
        return O0OOO0O0O0000OOO0 ._area #line:109
    def get_conf (OOOOO00OO000O0OO0 ):#line:111
        return OOOOO00OO000O0OO0 ._confidence #line:112
    def get_orientation (OO0OO00O0O0000OOO ,degree =False ):#line:114
        OO0OOOOO00O00OO0O =OO0OO00O0O0000OOO .get_xy ('left eye')#line:115
        O0O0OOO0O0O000OOO =OO0OO00O0O0000OOO .get_xy ('right eye')#line:116
        if degree :#line:117
            return Util .degree (OO0OOOOO00O00OO0O ,O0O0OOO0O0O000OOO )#line:118
        else :#line:119
            return Util .radian (OO0OOOOO00O00OO0O ,O0O0OOO0O0O000OOO )#line:120
    def crop (O00O0000000O0O000 ,O0O00000OO00OOOO0 ,clone =False ):#line:122
        if O0O00000OO00OOOO0 is None or O00O0000000O0O000 ._box is None :return None #line:123
        if clone :O0O00000OO00OOOO0 =O0O00000OO00OOOO0 .copy ()#line:124
        O0OOO00O000O0OOO0 =O00O0000000O0O000 ._box #line:125
        return O0O00000OO00OOOO0 [O0OOO00O000O0OOO0 [1 ]:O0OOO00O000O0OOO0 [3 ],O0OOO00O000O0OOO0 [0 ]:O0OOO00O000O0OOO0 [2 ]]#line:126
    @staticmethod #line:128
    def distance (OO0OOO000O0OO0OOO ,O00OOO0OOO000OO00 ):#line:129
        return Util .distance (OO0OOO000O0OO0OOO ,O00OOO0OOO000OO00 )#line:130
    @staticmethod #line:132
    def degree (OOO00O0OO000O000O ,OOOOOO00O000O00O0 ):#line:133
        return Util .degree (OOO00O0OO000O000O ,OOOOOO00O000O00O0 )#line:134
    @staticmethod #line:136
    def radian (O0O0000O000000O0O ,OO000O0OOOO0OO0OO ):#line:137
        return Util .radian (O0O0000O000000O0O ,OO000O0OOOO0OO0OO )#line:138
