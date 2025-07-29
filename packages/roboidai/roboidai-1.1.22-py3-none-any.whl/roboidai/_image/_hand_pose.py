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
from timeit import default_timer as timer #line:6
_O0OOO00O0O0OO00O0 =(0 ,1 ,2 ,5 ,9 ,13 ,17 )#line:9
_O0OO0OOO000O0O0O0 =[[0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,40 ,41 ,42 ,43 ,44 ,45 ,46 ,47 ],[8 ,9 ,10 ,11 ,12 ,13 ,14 ,15 ,48 ,49 ,50 ,51 ,52 ,53 ,54 ,55 ],[16 ,17 ,18 ,19 ,20 ,21 ,22 ,23 ,56 ,57 ,58 ,59 ,60 ,61 ,62 ,63 ],[24 ,25 ,26 ,27 ,28 ,29 ,30 ,31 ,64 ,65 ,66 ,67 ,68 ,69 ,70 ,71 ],[32 ,33 ,34 ,35 ,36 ,37 ,38 ,39 ,72 ,73 ,74 ,75 ,76 ,77 ,78 ,79 ]]#line:16
class HandPose :#line:19
    def __init__ (OO00O0OOO00OOO0O0 ):#line:20
        OO00O0OOO00OOO0O0 ._loaded =False #line:21
        OO00O0OOO00OOO0O0 ._both_hands =False #line:22
        OO00O0OOO00OOO0O0 ._left_hand_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(0 ,255 ,0 ),thickness =3 )#line:23
        OO00O0OOO00OOO0O0 ._right_hand_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(255 ,0 ,0 ),thickness =3 )#line:24
        OO00O0OOO00OOO0O0 ._both_hands_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(255 ,255 ,0 ),thickness =3 )#line:25
        OO00O0OOO00OOO0O0 ._landmark_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(0 ,0 ,255 ),circle_radius =3 )#line:26
        OO00O0OOO00OOO0O0 ._clear ()#line:27
    def _clear (OOO0OO00OO00OO000 ):#line:29
        OOO0OO00OO00OO000 ._points ={'left':{},'right':{}}#line:33
        OOO0OO00OO00OO000 ._boxes ={'left':{},'right':{}}#line:37
        OOO0OO00OO00OO000 ._widths ={'left':{},'right':{}}#line:41
        OOO0OO00OO00OO000 ._heights ={'left':{},'right':{}}#line:45
        OOO0OO00OO00OO000 ._areas ={'left':{},'right':{}}#line:49
        OOO0OO00OO00OO000 ._landmarks ={'left':None ,'right':None }#line:53
        OOO0OO00OO00OO000 ._is_right =[False ,False ]#line:54
        OOO0OO00OO00OO000 ._drawings =None #line:55
    def load_model (OOO00O0OO0OO000O0 ,both_hands =False ,threshold =0.5 ):#line:57
        OOO00O0OO0OO000O0 ._both_hands =both_hands #line:58
        try :#line:59
            OOOO000OO00OO0O00 =2 if both_hands else 1 #line:60
            OOO00O0OO0OO000O0 ._hands =mp .solutions .hands .Hands (max_num_hands =OOOO000OO00OO0O00 ,min_detection_confidence =threshold ,min_tracking_confidence =0.5 )#line:61
            OOO00O0OO0OO000O0 ._loaded =True #line:62
            return True #line:63
        except :#line:64
            return False #line:65
    def _calc_xyz (O00OO0000OO0OOOO0 ,O0OOOO00OO00OO0OO ,O000O0OOOOOOO00O0 ,O0000O0OO0000OO00 ,indices =None ):#line:67
        if indices is None :#line:68
            O00OO0000OO0OOOO0 ._points [O0OOOO00OO00OO0OO ][O000O0OOOOOOO00O0 ]=np .around (np .mean (O0000O0OO0000OO00 ,axis =0 )).astype (np .int32 )#line:69
        else :#line:70
            O00OO0000OO0OOOO0 ._points [O0OOOO00OO00OO0OO ][O000O0OOOOOOO00O0 ]=np .around (np .mean ([O0000O0OO0000OO00 [OOO000OOO00OOOO00 ]for OOO000OOO00OOOO00 in indices ],axis =0 )).astype (np .int32 )#line:71
    def _calc_box (OOOOO0O0O0O000OOO ,O0OO0O00OOO0000OO ,OO00O0000OOOOO0OO ,O0OO0OOO0OO00OOOO ,indices =None ):#line:73
        if indices is None :#line:74
            O000O0OO000O000O0 =np .min (O0OO0OOO0OO00OOOO ,axis =0 )#line:75
            O0O00OO0O0000OO0O =np .max (O0OO0OOO0OO00OOOO ,axis =0 )#line:76
        else :#line:77
            OOO0O00O0O0O0OO00 =[O0OO0OOO0OO00OOOO [O0000O0O0O0O0OOOO ]for O0000O0O0O0O0OOOO in indices ]#line:78
            O000O0OO000O000O0 =np .min (OOO0O00O0O0O0OO00 ,axis =0 )#line:79
            O0O00OO0O0000OO0O =np .max (OOO0O00O0O0O0OO00 ,axis =0 )#line:80
        OOOOO0O0O0O000OOO ._boxes [O0OO0O00OOO0000OO ][OO00O0000OOOOO0OO ]=[O000O0OO000O000O0 [0 ],O000O0OO000O000O0 [1 ],O0O00OO0O0000OO0O [0 ],O0O00OO0O0000OO0O [1 ]]#line:81
        OOOO0OO0O000OO000 =abs (O0O00OO0O0000OO0O [0 ]-O000O0OO000O000O0 [0 ])#line:82
        OOOO00OOO000O000O =abs (O0O00OO0O0000OO0O [1 ]-O000O0OO000O000O0 [1 ])#line:83
        OOOOO0O0O0O000OOO ._widths [O0OO0O00OOO0000OO ][OO00O0000OOOOO0OO ]=OOOO0OO0O000OO000 #line:84
        OOOOO0O0O0O000OOO ._heights [O0OO0O00OOO0000OO ][OO00O0000OOOOO0OO ]=OOOO00OOO000O000O #line:85
        OOOOO0O0O0O000OOO ._areas [O0OO0O00OOO0000OO ][OO00O0000OOOOO0OO ]=OOOO0OO0O000OO000 *OOOO00OOO000O000O #line:86
    def _calc_landmark (O0OOO0O0O0OO00O0O ,O000OO000OO00OO00 ,O0OO0OO000O0OO0OO ,O0OOOO00O0OOOOO00 ):#line:88
        O0OO0OO0OOO0O0OO0 =[OO0O0000O0OO0000O .x for OO0O0000O0OO0000O in O000OO000OO00OO00 .landmark ]#line:89
        OO00OOOOOO00OO0OO =[OOOO000000O00000O .y for OOOO000000O00000O in O000OO000OO00OO00 .landmark ]#line:90
        O0O000O0OO0000O00 =[OOOO00OO000O0000O .z for OOOO00OO000O0000O in O000OO000OO00OO00 .landmark ]#line:91
        OO0O0000O0OO0OO0O =np .transpose (np .stack ((O0OO0OO0OOO0O0OO0 ,OO00OOOOOO00OO0OO ,O0O000O0OO0000O00 )))*(O0OO0OO000O0OO0OO ,O0OOOO00O0OOOOO00 ,O0OO0OO000O0OO0OO )#line:92
        return OO0O0000O0OO0OO0O .astype (np .int32 )#line:93
    def _fill_data (OOO0O0000O00O0OOO ,O0O000O000OO0000O ,O0OOOO0O0O0OO00OO ):#line:95
        OOO0O0000O00O0OOO ._landmarks [O0O000O000OO0000O ]=O0OOOO0O0O0OO00OO #line:96
        OOO0O0000O00O0OOO ._calc_box (O0O000O000OO0000O ,'hand',O0OOOO0O0O0OO00OO )#line:97
        OOO0O0000O00O0OOO ._calc_box (O0O000O000OO0000O ,'palm',O0OOOO0O0O0OO00OO ,_O0OOO00O0O0OO00O0 )#line:98
        OOO0O0000O00O0OOO ._calc_xyz (O0O000O000OO0000O ,'hand',O0OOOO0O0O0OO00OO )#line:99
        OOO0O0000O00O0OOO ._calc_xyz (O0O000O000OO0000O ,'palm',O0OOOO0O0O0OO00OO ,_O0OOO00O0O0OO00O0 )#line:100
    def detect (O0OO0000OO000OO0O ,O0O00OOOOO0OO0O0O ):#line:102
        if O0O00OOOOO0OO0O0O is not None and O0OO0000OO000OO0O ._loaded :#line:103
            O0O00OOOOO0OO0O0O =cv2 .cvtColor (O0O00OOOOO0OO0O0O ,cv2 .COLOR_BGR2RGB )#line:104
            O0O00OOOOO0OO0O0O .flags .writeable =False #line:105
            OO0000OOOOO0OO00O =O0OO0000OO000OO0O ._hands .process (O0O00OOOOO0OO0O0O )#line:106
            if OO0000OOOOO0OO00O and OO0000OOOOO0OO00O .multi_hand_landmarks and len (OO0000OOOOO0OO00O .multi_hand_landmarks )>0 and OO0000OOOOO0OO00O .multi_handedness and len (OO0000OOOOO0OO00O .multi_handedness )>0 :#line:107
                O00OOOOO00000O0OO =O0O00OOOOO0OO0O0O .shape [1 ]#line:108
                O0O0O0OO0OO00O0O0 =O0O00OOOOO0OO0O0O .shape [0 ]#line:109
                if O0OO0000OO000OO0O ._both_hands :#line:110
                    O0OO0O0OOOO00O00O =True #line:111
                    O00O00O0O0000O00O =True #line:112
                    O00OOO0OOOO0OO00O =OO0000OOOOO0OO00O .multi_hand_landmarks [0 ]#line:113
                    if len (O00OOO0OOOO0OO00O .landmark )==21 :#line:114
                        O00OO000OOOO00000 =O0OO0000OO000OO0O ._calc_landmark (O00OOO0OOOO0OO00O ,O00OOOOO00000O0OO ,O0O0O0OO0OO00O0O0 )#line:115
                        O0OOOOO0OOO0000O0 =OO0000OOOOO0OO00O .multi_handedness [0 ].classification .pop ()#line:116
                        if O0OOOOO0OOO0000O0 and O0OOOOO0OOO0000O0 .label =='Left':#line:117
                            O0OO0000OO000OO0O ._is_right [0 ]=False #line:118
                            O0OO0000OO000OO0O ._fill_data ('left',O00OO000OOOO00000 )#line:119
                        else :#line:120
                            O0OO0000OO000OO0O ._is_right [0 ]=True #line:121
                            O0OO0000OO000OO0O ._fill_data ('right',O00OO000OOOO00000 )#line:122
                    else :#line:123
                        O0OO0O0OOOO00O00O =False #line:124
                    if len (OO0000OOOOO0OO00O .multi_hand_landmarks )>1 and len (OO0000OOOOO0OO00O .multi_handedness )>1 :#line:125
                        O0O0000O0O0O000O0 =OO0000OOOOO0OO00O .multi_hand_landmarks [1 ]#line:126
                        if len (O0O0000O0O0O000O0 .landmark )==21 :#line:127
                            O00OO000OOOO00000 =O0OO0000OO000OO0O ._calc_landmark (O0O0000O0O0O000O0 ,O00OOOOO00000O0OO ,O0O0O0OO0OO00O0O0 )#line:128
                            O0OOOOO0OOO0000O0 =OO0000OOOOO0OO00O .multi_handedness [1 ].classification .pop ()#line:129
                            if O0OOOOO0OOO0000O0 and O0OOOOO0OOO0000O0 .label =='Left':#line:130
                                O0OO0000OO000OO0O ._is_right [1 ]=False #line:131
                                O0OO0000OO000OO0O ._fill_data ('left',O00OO000OOOO00000 )#line:132
                            else :#line:133
                                O0OO0000OO000OO0O ._is_right [1 ]=True #line:134
                                O0OO0000OO000OO0O ._fill_data ('right',O00OO000OOOO00000 )#line:135
                        else :#line:136
                            O00O00O0O0000O00O =False #line:137
                    if O0OO0O0OOOO00O00O and O00O00O0O0000O00O :#line:138
                        O0OO0000OO000OO0O ._drawings =OO0000OOOOO0OO00O #line:139
                        return True #line:140
                else :#line:141
                    OO0OOOOOO00OO000O =OO0000OOOOO0OO00O .multi_hand_landmarks [0 ]#line:142
                    if len (OO0OOOOOO00OO000O .landmark )==21 :#line:143
                        O00OO000OOOO00000 =O0OO0000OO000OO0O ._calc_landmark (OO0OOOOOO00OO000O ,O00OOOOO00000O0OO ,O0O0O0OO0OO00O0O0 )#line:144
                        O0OO0000OO000OO0O ._fill_data ('left',O00OO000OOOO00000 )#line:145
                        O0OO0000OO000OO0O ._fill_data ('right',O00OO000OOOO00000 )#line:146
                        O0OO0000OO000OO0O ._drawings =OO0000OOOOO0OO00O #line:147
                        return True #line:148
        O0OO0000OO000OO0O ._clear ()#line:149
        return False #line:150
    def draw_result (O00000OO0O00000O0 ,O0O0O0O0OOOOOO0O0 ,clone =False ):#line:152
        O0OOOOOO0OO0000OO =O00000OO0O00000O0 ._drawings #line:153
        if O0O0O0O0OOOOOO0O0 is not None and O0OOOOOO0OO0000OO is not None and O0OOOOOO0OO0000OO .multi_hand_landmarks and len (O0OOOOOO0OO0000OO .multi_hand_landmarks )>0 :#line:154
            if clone :#line:155
                O0O0O0O0OOOOOO0O0 =O0O0O0O0OOOOOO0O0 .copy ()#line:156
            if O00000OO0O00000O0 ._both_hands :#line:157
                OOOOO000OO000OO0O =O0OOOOOO0OO0000OO .multi_hand_landmarks [0 ]#line:158
                O00000OO00OOO0000 =O00000OO0O00000O0 ._right_hand_drawing_spec if O00000OO0O00000O0 ._is_right [0 ]else O00000OO0O00000O0 ._left_hand_drawing_spec #line:159
                mp .solutions .drawing_utils .draw_landmarks (O0O0O0O0OOOOOO0O0 ,OOOOO000OO000OO0O ,mp .solutions .hands .HAND_CONNECTIONS ,O00000OO0O00000O0 ._landmark_drawing_spec ,O00000OO00OOO0000 )#line:160
                if len (O0OOOOOO0OO0000OO .multi_hand_landmarks )>1 :#line:161
                    OOOOO000OO000OO0O =O0OOOOOO0OO0000OO .multi_hand_landmarks [1 ]#line:162
                    O00000OO00OOO0000 =O00000OO0O00000O0 ._right_hand_drawing_spec if O00000OO0O00000O0 ._is_right [1 ]else O00000OO0O00000O0 ._left_hand_drawing_spec #line:163
                    mp .solutions .drawing_utils .draw_landmarks (O0O0O0O0OOOOOO0O0 ,OOOOO000OO000OO0O ,mp .solutions .hands .HAND_CONNECTIONS ,O00000OO0O00000O0 ._landmark_drawing_spec ,O00000OO00OOO0000 )#line:164
            else :#line:165
                mp .solutions .drawing_utils .draw_landmarks (O0O0O0O0OOOOOO0O0 ,O0OOOOOO0OO0000OO .multi_hand_landmarks [0 ],mp .solutions .hands .HAND_CONNECTIONS ,O00000OO0O00000O0 ._landmark_drawing_spec ,O00000OO0O00000O0 ._both_hands_drawing_spec )#line:166
        return O0O0O0O0OOOOOO0O0 #line:167
    def get_xy (OOOO000O0OO00O0OO ,OO00000O0OO0OOO0O ,id ='all',index =0 ):#line:169
        O00O0OO00000OO000 =OOOO000O0OO00O0OO .get_xyz (OO00000O0OO0OOO0O ,id ,index )#line:170
        if O00O0OO00000OO000 is None :return None #line:171
        if O00O0OO00000OO000 .ndim ==1 :#line:172
            return O00O0OO00000OO000 [:2 ]#line:173
        elif O00O0OO00000OO000 .ndim ==2 :#line:174
            return O00O0OO00000OO000 [:,:2 ]#line:175
        return None #line:176
    def get_xyz (O00OOOO0000OO0OOO ,OO0OOOO000O00OOOO ,id ='all',index =0 ):#line:178
        if isinstance (id ,(int ,float )):#line:179
            if O00OOOO0000OO0OOO ._landmarks [OO0OOOO000O00OOOO ]is None :return None #line:180
            id =int (id )#line:181
            if id ==0 :return O00OOOO0000OO0OOO ._landmarks [OO0OOOO000O00OOOO ][0 ]#line:182
            id =(id -1 )*4 +(3 -index )+1 #line:183
            if id <0 or id >20 :return None #line:184
            return O00OOOO0000OO0OOO ._landmarks [OO0OOOO000O00OOOO ][id ]#line:185
        elif isinstance (id ,str ):#line:186
            id =id .lower ()#line:187
            if id =='all':#line:188
                return O00OOOO0000OO0OOO ._landmarks [OO0OOOO000O00OOOO ]#line:189
            elif id in O00OOOO0000OO0OOO ._points [OO0OOOO000O00OOOO ]:#line:190
                return O00OOOO0000OO0OOO ._points [OO0OOOO000O00OOOO ][id ]#line:191
        return None #line:192
    def get_box (O00O0OOO00OO0000O ,O0O0000OOO000OOOO ,id ='all'):#line:194
        if isinstance (id ,str ):#line:195
            id =id .lower ()#line:196
            if id =='all':#line:197
                return O00O0OOO00OO0000O ._boxes [O0O0000OOO000OOOO ]#line:198
            elif id in O00O0OOO00OO0000O ._boxes [O0O0000OOO000OOOO ]:#line:199
                return O00O0OOO00OO0000O ._boxes [O0O0000OOO000OOOO ][id ]#line:200
        return None #line:201
    def get_width (O000OOOO00O0000OO ,OOOO0OO0O0O00000O ,id ='all'):#line:203
        if isinstance (id ,str ):#line:204
            id =id .lower ()#line:205
            if id =='all':#line:206
                return O000OOOO00O0000OO ._widths [OOOO0OO0O0O00000O ]#line:207
            elif id in O000OOOO00O0000OO ._widths [OOOO0OO0O0O00000O ]:#line:208
                return O000OOOO00O0000OO ._widths [OOOO0OO0O0O00000O ][id ]#line:209
        return 0 #line:210
    def get_height (OOO0O000OO0O00O00 ,OOO0O0OO00OO0OO0O ,id ='all'):#line:212
        if isinstance (id ,str ):#line:213
            id =id .lower ()#line:214
            if id =='all':#line:215
                return OOO0O000OO0O00O00 ._heights [OOO0O0OO00OO0OO0O ]#line:216
            elif id in OOO0O000OO0O00O00 ._heights [OOO0O0OO00OO0OO0O ]:#line:217
                return OOO0O000OO0O00O00 ._heights [OOO0O0OO00OO0OO0O ][id ]#line:218
        return 0 #line:219
    def get_area (O0OO0O0O0O000O000 ,O0OOOO0OO000O000O ,id ='all'):#line:221
        if isinstance (id ,str ):#line:222
            id =id .lower ()#line:223
            if id =='all':#line:224
                return O0OO0O0O0O000O000 ._areas [O0OOOO0OO000O000O ]#line:225
            elif id in O0OO0O0O0O000O000 ._areas [O0OOOO0OO000O000O ]:#line:226
                return O0OO0O0O0O000O000 ._areas [O0OOOO0OO000O000O ][id ]#line:227
        return 0 #line:228
    def get_feature (O00O0O000O00O0O00 ,filter ='all'):#line:230
        OOOO0O00O0OOOO000 =O00O0O000O00O0O00 .get_width ('left','palm')#line:231
        O0OOO0OOOOO00OO0O =O00O0O000O00O0O00 .get_height ('left','palm')#line:232
        O000O00OOOO00O0O0 =[OOOO0O00O0OOOO000 ,O0OOO0OOOOO00OO0O ]#line:233
        if OOOO0O00O0OOOO000 >0 and O0OOO0OOOOO00OO0O >0 :#line:234
            O00O000O0OO0O00O0 =O00O0O000O00O0O00 ._landmarks ['left']#line:235
            O0O0O000OO0O0O0OO =O00O0O000O00O0O00 ._landmarks ['right']#line:236
            if O00O000O0OO0O00O0 is not None and O0O0O000OO0O0O0OO is not None :#line:237
                OO00O0OO0OOOOOOOO =O00O000O0OO0O00O0 [0 ,:2 ]#line:238
                O00O000O0OO0O00O0 =(O00O000O0OO0O00O0 [1 :,:2 ]-OO00O0OO0OOOOOOOO )/O000O00OOOO00O0O0 #line:239
                OO00O0OO0OOOOOOOO =O0O0O000OO0O0O0OO [0 ,:2 ]#line:240
                O0O0O000OO0O0O0OO =(O0O0O000OO0O0O0OO [1 :,:2 ]-OO00O0OO0OOOOOOOO )/O000O00OOOO00O0O0 #line:241
                OOOOOOO0000O0O0OO =np .concatenate ((O00O000O0OO0O00O0 .reshape (-1 ),O0O0O000OO0O0O0OO .reshape (-1 )),axis =None )#line:242
                if isinstance (filter ,str ):#line:243
                    filter =filter .lower ()#line:244
                    if filter =='all':#line:245
                        return OOOOOOO0000O0O0OO #line:246
                elif isinstance (filter ,(int ,float )):#line:247
                    filter =int (filter )#line:248
                    if filter >0 and filter <6 :#line:249
                        O0OO000O0OO000OOO =_O0OO0OOO000O0O0O0 [filter -1 ]#line:250
                        return np .array ([OOOOOOO0000O0O0OO [O00OOOO000OO00OOO ]for O00OOOO000OO00OOO in O0OO000O0OO000OOO ])#line:251
                elif isinstance (filter ,(list ,tuple )):#line:252
                    O0OO000O0OO000OOO =[]#line:253
                    for OOOOOOOO0O0OO0O0O in filter :#line:254
                        if isinstance (OOOOOOOO0O0OO0O0O ,(int ,float )):#line:255
                            OOOOOOOO0O0OO0O0O =int (OOOOOOOO0O0OO0O0O )#line:256
                            if OOOOOOOO0O0OO0O0O >0 and OOOOOOOO0O0OO0O0O <6 :#line:257
                                O0OO000O0OO000OOO .extend (_O0OO0OOO000O0O0O0 [OOOOOOOO0O0OO0O0O -1 ])#line:258
                    return np .array ([OOOOOOO0000O0O0OO [O0O0000O0000OO000 ]for O0O0000O0000OO000 in O0OO000O0OO000OOO ])#line:259
        return None #line:260
    def _get_feature_label (O0O0OO00O0OOOO00O ,filter ='all'):#line:262
        if isinstance (filter ,str ):#line:263
            filter =filter .lower ()#line:264
            if filter =='all':#line:265
                return ['f'+str (O0OOO0OOOOO0OOOOO )for O0OOO0OOOOO0OOOOO in range (80 )]#line:266
        elif isinstance (filter ,(int ,float )):#line:267
            filter =int (filter )#line:268
            if filter >0 and filter <6 :#line:269
                OOOO0OO000O0O00O0 =_O0OO0OOO000O0O0O0 [filter -1 ]#line:270
                return ['f'+str (O00O000O0O0O0O00O )for O00O000O0O0O0O00O in OOOO0OO000O0O00O0 ]#line:271
        elif isinstance (filter ,(list ,tuple )):#line:272
            OOOO0OO000O0O00O0 =[]#line:273
            for O0OOOO00O0O00OOO0 in filter :#line:274
                if isinstance (O0OOOO00O0O00OOO0 ,(int ,float )):#line:275
                    O0OOOO00O0O00OOO0 =int (O0OOOO00O0O00OOO0 )#line:276
                    if O0OOOO00O0O00OOO0 >0 and O0OOOO00O0O00OOO0 <6 :#line:277
                        OOOO0OO000O0O00O0 .extend (_O0OO0OOO000O0O0O0 [O0OOOO00O0O00OOO0 -1 ])#line:278
            return ['f'+str (OO0O0OOO0OO0OO000 )for OO0O0OOO0OO0OO000 in OOOO0OO000O0O00O0 ]#line:279
    def record_feature (O000OO0000000O0OO ,O000OO0OOOO0O0OO0 ,O0O0OO0OOO0OO0O0O ,filter ='all',interval_msec =100 ,frames =20 ,countdown =3 ):#line:281
        if countdown >0 :#line:282
            O000OO0OOOO0O0OO0 .count_down (countdown )#line:283
        OOO00O0O0OOO0000O =0 #line:284
        OO0OOOOO0000OOO0O =timer ()#line:285
        OO00OO000OO0OO00O =','.join (O000OO0000000O0OO ._get_feature_label (filter ))#line:286
        OO0O000O000OO0OOO =[]#line:287
        while True :#line:288
            if OOO00O0O0OOO0000O >=frames :break #line:289
            OOOOO0000O00OO00O =O000OO0OOOO0O0OO0 .read ()#line:290
            if O000OO0000000O0OO .detect (OOOOO0000O00OO00O ):#line:291
                OOOOO0000O00OO00O =O000OO0000000O0OO .draw_result (OOOOO0000O00OO00O )#line:292
                if timer ()>OO0OOOOO0000OOO0O :#line:293
                    OO0O000O000OO0OOO .append (O000OO0000000O0OO .get_feature (filter ))#line:294
                    OOO00O0O0OOO0000O +=1 #line:295
                    print ('saved',OOO00O0O0OOO0000O )#line:296
                    OO0OOOOO0000OOO0O +=interval_msec /1000.0 #line:297
                if O000OO0OOOO0O0OO0 .check_key ()=='esc':#line:298
                    return #line:299
            O000OO0OOOO0O0OO0 .show (OOOOO0000O00OO00O )#line:300
        if O0O0OO0OOO0OO0O0O is not None :#line:301
            Util .realize_filepath (O0O0OO0OOO0OO0O0O )#line:302
            np .savetxt (O0O0OO0OOO0OO0O0O ,OO0O000O000OO0OOO ,fmt ='%f',delimiter =',',header =OO00OO000OO0OO00O ,comments ='')#line:303
    @staticmethod #line:305
    def distance (OOOOO0OOO0O0O0OOO ,O00O0OO000O000O00 ):#line:306
        return Util .distance (OOOOO0OOO0O0O0OOO ,O00O0OO000O000O00 )#line:307
    @staticmethod #line:309
    def degree (O0OOO0OOOOOOO00OO ,OOO000000OOO00000 ):#line:310
        return Util .degree (O0OOO0OOOOOOO00OO ,OOO000000OOO00000 )#line:311
    @staticmethod #line:313
    def radian (O000000OOOOO0O000 ,OO0O00O0OO000OOOO ):#line:314
        return Util .radian (O000000OOOOO0O000 ,OO0O00O0OO000OOOO )#line:315
