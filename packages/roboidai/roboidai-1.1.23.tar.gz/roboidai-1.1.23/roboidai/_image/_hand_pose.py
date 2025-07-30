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
_O0O0OOOOOO00OO0O0 =(0 ,1 ,2 ,5 ,9 ,13 ,17 )#line:9
_O000OOOO0O0OO0O0O =[[0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,40 ,41 ,42 ,43 ,44 ,45 ,46 ,47 ],[8 ,9 ,10 ,11 ,12 ,13 ,14 ,15 ,48 ,49 ,50 ,51 ,52 ,53 ,54 ,55 ],[16 ,17 ,18 ,19 ,20 ,21 ,22 ,23 ,56 ,57 ,58 ,59 ,60 ,61 ,62 ,63 ],[24 ,25 ,26 ,27 ,28 ,29 ,30 ,31 ,64 ,65 ,66 ,67 ,68 ,69 ,70 ,71 ],[32 ,33 ,34 ,35 ,36 ,37 ,38 ,39 ,72 ,73 ,74 ,75 ,76 ,77 ,78 ,79 ]]#line:16
class HandPose :#line:19
    def __init__ (OOOO0OOO0O00000O0 ):#line:20
        OOOO0OOO0O00000O0 ._loaded =False #line:21
        OOOO0OOO0O00000O0 ._both_hands =False #line:22
        OOOO0OOO0O00000O0 ._left_hand_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(0 ,255 ,0 ),thickness =3 )#line:23
        OOOO0OOO0O00000O0 ._right_hand_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(255 ,0 ,0 ),thickness =3 )#line:24
        OOOO0OOO0O00000O0 ._both_hands_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(255 ,255 ,0 ),thickness =3 )#line:25
        OOOO0OOO0O00000O0 ._landmark_drawing_spec =mp .solutions .drawing_utils .DrawingSpec (color =(0 ,0 ,255 ),circle_radius =3 )#line:26
        OOOO0OOO0O00000O0 ._clear ()#line:27
    def _clear (O00OOO0O00O00OO0O ):#line:29
        O00OOO0O00O00OO0O ._points ={'left':{},'right':{}}#line:33
        O00OOO0O00O00OO0O ._boxes ={'left':{},'right':{}}#line:37
        O00OOO0O00O00OO0O ._widths ={'left':{},'right':{}}#line:41
        O00OOO0O00O00OO0O ._heights ={'left':{},'right':{}}#line:45
        O00OOO0O00O00OO0O ._areas ={'left':{},'right':{}}#line:49
        O00OOO0O00O00OO0O ._landmarks ={'left':None ,'right':None }#line:53
        O00OOO0O00O00OO0O ._is_right =[False ,False ]#line:54
        O00OOO0O00O00OO0O ._drawings =None #line:55
    def load_model (O0000O00OO000O00O ,both_hands =False ,threshold =0.5 ):#line:57
        O0000O00OO000O00O ._both_hands =both_hands #line:58
        try :#line:59
            OOO0OO0O000OO00O0 =2 if both_hands else 1 #line:60
            O0000O00OO000O00O ._hands =mp .solutions .hands .Hands (max_num_hands =OOO0OO0O000OO00O0 ,min_detection_confidence =threshold ,min_tracking_confidence =0.5 )#line:61
            O0000O00OO000O00O ._loaded =True #line:62
            return True #line:63
        except :#line:64
            return False #line:65
    def _calc_xyz (OOOO0000O0000O0O0 ,OOOO0000000OO0O00 ,OOO0OOOO00O00OOOO ,OOO0O00OOOO0O00OO ,indices =None ):#line:67
        if indices is None :#line:68
            OOOO0000O0000O0O0 ._points [OOOO0000000OO0O00 ][OOO0OOOO00O00OOOO ]=np .around (np .mean (OOO0O00OOOO0O00OO ,axis =0 )).astype (np .int32 )#line:69
        else :#line:70
            OOOO0000O0000O0O0 ._points [OOOO0000000OO0O00 ][OOO0OOOO00O00OOOO ]=np .around (np .mean ([OOO0O00OOOO0O00OO [O000O0O000OOO0O00 ]for O000O0O000OOO0O00 in indices ],axis =0 )).astype (np .int32 )#line:71
    def _calc_box (O0OOOOOOO0O0O0OOO ,OO0O0OO0000OO000O ,OOO0OOO0O00O000OO ,OO00O0OO0OO0O0OO0 ,indices =None ):#line:73
        if indices is None :#line:74
            OO00O0O000O000O0O =np .min (OO00O0OO0OO0O0OO0 ,axis =0 )#line:75
            OO00O0O0OOO0O00OO =np .max (OO00O0OO0OO0O0OO0 ,axis =0 )#line:76
        else :#line:77
            OOOO0O00O000O0000 =[OO00O0OO0OO0O0OO0 [O0O0O0O0O0OOOOOOO ]for O0O0O0O0O0OOOOOOO in indices ]#line:78
            OO00O0O000O000O0O =np .min (OOOO0O00O000O0000 ,axis =0 )#line:79
            OO00O0O0OOO0O00OO =np .max (OOOO0O00O000O0000 ,axis =0 )#line:80
        O0OOOOOOO0O0O0OOO ._boxes [OO0O0OO0000OO000O ][OOO0OOO0O00O000OO ]=[OO00O0O000O000O0O [0 ],OO00O0O000O000O0O [1 ],OO00O0O0OOO0O00OO [0 ],OO00O0O0OOO0O00OO [1 ]]#line:81
        OOOOOOO0O0000OO00 =abs (OO00O0O0OOO0O00OO [0 ]-OO00O0O000O000O0O [0 ])#line:82
        O00OO00O000OOO0O0 =abs (OO00O0O0OOO0O00OO [1 ]-OO00O0O000O000O0O [1 ])#line:83
        O0OOOOOOO0O0O0OOO ._widths [OO0O0OO0000OO000O ][OOO0OOO0O00O000OO ]=OOOOOOO0O0000OO00 #line:84
        O0OOOOOOO0O0O0OOO ._heights [OO0O0OO0000OO000O ][OOO0OOO0O00O000OO ]=O00OO00O000OOO0O0 #line:85
        O0OOOOOOO0O0O0OOO ._areas [OO0O0OO0000OO000O ][OOO0OOO0O00O000OO ]=OOOOOOO0O0000OO00 *O00OO00O000OOO0O0 #line:86
    def _calc_landmark (O0O0OOOO0OO0O0OOO ,OOO0OO0OO000OO000 ,O000OOO00000O0OO0 ,OO00O0OO0OO000OOO ):#line:88
        OO0O0O0O000O0OOOO =[O0OOO0O0O000OO00O .x for O0OOO0O0O000OO00O in OOO0OO0OO000OO000 .landmark ]#line:89
        O00O0OOO0O00OOO0O =[O0O00O0000O0OO0O0 .y for O0O00O0000O0OO0O0 in OOO0OO0OO000OO000 .landmark ]#line:90
        OOO0OOO0O0OOOO000 =[O0OO0OOOO00O0OO0O .z for O0OO0OOOO00O0OO0O in OOO0OO0OO000OO000 .landmark ]#line:91
        O00O00OOO0OOOO0OO =np .transpose (np .stack ((OO0O0O0O000O0OOOO ,O00O0OOO0O00OOO0O ,OOO0OOO0O0OOOO000 )))*(O000OOO00000O0OO0 ,OO00O0OO0OO000OOO ,O000OOO00000O0OO0 )#line:92
        return O00O00OOO0OOOO0OO .astype (np .int32 )#line:93
    def _fill_data (OO0O0000OOOO0OO00 ,O000O0OOOO0OO00O0 ,OO0O00OO0O000OOO0 ):#line:95
        OO0O0000OOOO0OO00 ._landmarks [O000O0OOOO0OO00O0 ]=OO0O00OO0O000OOO0 #line:96
        OO0O0000OOOO0OO00 ._calc_box (O000O0OOOO0OO00O0 ,'hand',OO0O00OO0O000OOO0 )#line:97
        OO0O0000OOOO0OO00 ._calc_box (O000O0OOOO0OO00O0 ,'palm',OO0O00OO0O000OOO0 ,_O0O0OOOOOO00OO0O0 )#line:98
        OO0O0000OOOO0OO00 ._calc_xyz (O000O0OOOO0OO00O0 ,'hand',OO0O00OO0O000OOO0 )#line:99
        OO0O0000OOOO0OO00 ._calc_xyz (O000O0OOOO0OO00O0 ,'palm',OO0O00OO0O000OOO0 ,_O0O0OOOOOO00OO0O0 )#line:100
    def detect (OO0OO0OO0OO0OO00O ,OO000O0OOOO0O0O0O ):#line:102
        if OO000O0OOOO0O0O0O is not None and OO0OO0OO0OO0OO00O ._loaded :#line:103
            OO000O0OOOO0O0O0O =cv2 .cvtColor (OO000O0OOOO0O0O0O ,cv2 .COLOR_BGR2RGB )#line:104
            OO000O0OOOO0O0O0O .flags .writeable =False #line:105
            O0OOO0000OOO0OOO0 =OO0OO0OO0OO0OO00O ._hands .process (OO000O0OOOO0O0O0O )#line:106
            if O0OOO0000OOO0OOO0 and O0OOO0000OOO0OOO0 .multi_hand_landmarks and len (O0OOO0000OOO0OOO0 .multi_hand_landmarks )>0 and O0OOO0000OOO0OOO0 .multi_handedness and len (O0OOO0000OOO0OOO0 .multi_handedness )>0 :#line:107
                O00000O00O0O0O0O0 =OO000O0OOOO0O0O0O .shape [1 ]#line:108
                O0O0O0O00O0OOOO0O =OO000O0OOOO0O0O0O .shape [0 ]#line:109
                if OO0OO0OO0OO0OO00O ._both_hands :#line:110
                    O000O000OOOO0OO0O =True #line:111
                    OOOO0OO00000O0O0O =True #line:112
                    OO00OO0O0O0O0O000 =O0OOO0000OOO0OOO0 .multi_hand_landmarks [0 ]#line:113
                    if len (OO00OO0O0O0O0O000 .landmark )==21 :#line:114
                        OO0OOO00O000O0000 =OO0OO0OO0OO0OO00O ._calc_landmark (OO00OO0O0O0O0O000 ,O00000O00O0O0O0O0 ,O0O0O0O00O0OOOO0O )#line:115
                        O000OOOO0OO0O0OO0 =O0OOO0000OOO0OOO0 .multi_handedness [0 ].classification .pop ()#line:116
                        if O000OOOO0OO0O0OO0 and O000OOOO0OO0O0OO0 .label =='Left':#line:117
                            OO0OO0OO0OO0OO00O ._is_right [0 ]=False #line:118
                            OO0OO0OO0OO0OO00O ._fill_data ('left',OO0OOO00O000O0000 )#line:119
                        else :#line:120
                            OO0OO0OO0OO0OO00O ._is_right [0 ]=True #line:121
                            OO0OO0OO0OO0OO00O ._fill_data ('right',OO0OOO00O000O0000 )#line:122
                    else :#line:123
                        O000O000OOOO0OO0O =False #line:124
                    if len (O0OOO0000OOO0OOO0 .multi_hand_landmarks )>1 and len (O0OOO0000OOO0OOO0 .multi_handedness )>1 :#line:125
                        OOO00OO00OOO00O0O =O0OOO0000OOO0OOO0 .multi_hand_landmarks [1 ]#line:126
                        if len (OOO00OO00OOO00O0O .landmark )==21 :#line:127
                            OO0OOO00O000O0000 =OO0OO0OO0OO0OO00O ._calc_landmark (OOO00OO00OOO00O0O ,O00000O00O0O0O0O0 ,O0O0O0O00O0OOOO0O )#line:128
                            O000OOOO0OO0O0OO0 =O0OOO0000OOO0OOO0 .multi_handedness [1 ].classification .pop ()#line:129
                            if O000OOOO0OO0O0OO0 and O000OOOO0OO0O0OO0 .label =='Left':#line:130
                                OO0OO0OO0OO0OO00O ._is_right [1 ]=False #line:131
                                OO0OO0OO0OO0OO00O ._fill_data ('left',OO0OOO00O000O0000 )#line:132
                            else :#line:133
                                OO0OO0OO0OO0OO00O ._is_right [1 ]=True #line:134
                                OO0OO0OO0OO0OO00O ._fill_data ('right',OO0OOO00O000O0000 )#line:135
                        else :#line:136
                            OOOO0OO00000O0O0O =False #line:137
                    if O000O000OOOO0OO0O and OOOO0OO00000O0O0O :#line:138
                        OO0OO0OO0OO0OO00O ._drawings =O0OOO0000OOO0OOO0 #line:139
                        return True #line:140
                else :#line:141
                    O0OOOO0O000OO000O =O0OOO0000OOO0OOO0 .multi_hand_landmarks [0 ]#line:142
                    if len (O0OOOO0O000OO000O .landmark )==21 :#line:143
                        OO0OOO00O000O0000 =OO0OO0OO0OO0OO00O ._calc_landmark (O0OOOO0O000OO000O ,O00000O00O0O0O0O0 ,O0O0O0O00O0OOOO0O )#line:144
                        OO0OO0OO0OO0OO00O ._fill_data ('left',OO0OOO00O000O0000 )#line:145
                        OO0OO0OO0OO0OO00O ._fill_data ('right',OO0OOO00O000O0000 )#line:146
                        OO0OO0OO0OO0OO00O ._drawings =O0OOO0000OOO0OOO0 #line:147
                        return True #line:148
        OO0OO0OO0OO0OO00O ._clear ()#line:149
        return False #line:150
    def draw_result (OOO0O0O0O000OOO00 ,OOOO000OO00O000O0 ,clone =False ):#line:152
        OO0OO0OOO0O00O0OO =OOO0O0O0O000OOO00 ._drawings #line:153
        if OOOO000OO00O000O0 is not None and OO0OO0OOO0O00O0OO is not None and OO0OO0OOO0O00O0OO .multi_hand_landmarks and len (OO0OO0OOO0O00O0OO .multi_hand_landmarks )>0 :#line:154
            if clone :#line:155
                OOOO000OO00O000O0 =OOOO000OO00O000O0 .copy ()#line:156
            if OOO0O0O0O000OOO00 ._both_hands :#line:157
                OOO00OO0O0000O000 =OO0OO0OOO0O00O0OO .multi_hand_landmarks [0 ]#line:158
                OO0OOOO0O00000000 =OOO0O0O0O000OOO00 ._right_hand_drawing_spec if OOO0O0O0O000OOO00 ._is_right [0 ]else OOO0O0O0O000OOO00 ._left_hand_drawing_spec #line:159
                mp .solutions .drawing_utils .draw_landmarks (OOOO000OO00O000O0 ,OOO00OO0O0000O000 ,mp .solutions .hands .HAND_CONNECTIONS ,OOO0O0O0O000OOO00 ._landmark_drawing_spec ,OO0OOOO0O00000000 )#line:160
                if len (OO0OO0OOO0O00O0OO .multi_hand_landmarks )>1 :#line:161
                    OOO00OO0O0000O000 =OO0OO0OOO0O00O0OO .multi_hand_landmarks [1 ]#line:162
                    OO0OOOO0O00000000 =OOO0O0O0O000OOO00 ._right_hand_drawing_spec if OOO0O0O0O000OOO00 ._is_right [1 ]else OOO0O0O0O000OOO00 ._left_hand_drawing_spec #line:163
                    mp .solutions .drawing_utils .draw_landmarks (OOOO000OO00O000O0 ,OOO00OO0O0000O000 ,mp .solutions .hands .HAND_CONNECTIONS ,OOO0O0O0O000OOO00 ._landmark_drawing_spec ,OO0OOOO0O00000000 )#line:164
            else :#line:165
                mp .solutions .drawing_utils .draw_landmarks (OOOO000OO00O000O0 ,OO0OO0OOO0O00O0OO .multi_hand_landmarks [0 ],mp .solutions .hands .HAND_CONNECTIONS ,OOO0O0O0O000OOO00 ._landmark_drawing_spec ,OOO0O0O0O000OOO00 ._both_hands_drawing_spec )#line:166
        return OOOO000OO00O000O0 #line:167
    def get_xy (OO0O0OOO000O0OOO0 ,OOOOOOOOOO0OOO000 ,id ='all',index =0 ):#line:169
        OO00OO00OOO0000O0 =OO0O0OOO000O0OOO0 .get_xyz (OOOOOOOOOO0OOO000 ,id ,index )#line:170
        if OO00OO00OOO0000O0 is None :return None #line:171
        if OO00OO00OOO0000O0 .ndim ==1 :#line:172
            return OO00OO00OOO0000O0 [:2 ]#line:173
        elif OO00OO00OOO0000O0 .ndim ==2 :#line:174
            return OO00OO00OOO0000O0 [:,:2 ]#line:175
        return None #line:176
    def get_xyz (OOO00OOO0OOOO00O0 ,O0OOOO00OOO0OOO00 ,id ='all',index =0 ):#line:178
        if isinstance (id ,(int ,float )):#line:179
            if OOO00OOO0OOOO00O0 ._landmarks [O0OOOO00OOO0OOO00 ]is None :return None #line:180
            id =int (id )#line:181
            if id ==0 :return OOO00OOO0OOOO00O0 ._landmarks [O0OOOO00OOO0OOO00 ][0 ]#line:182
            id =(id -1 )*4 +(3 -index )+1 #line:183
            if id <0 or id >20 :return None #line:184
            return OOO00OOO0OOOO00O0 ._landmarks [O0OOOO00OOO0OOO00 ][id ]#line:185
        elif isinstance (id ,str ):#line:186
            id =id .lower ()#line:187
            if id =='all':#line:188
                return OOO00OOO0OOOO00O0 ._landmarks [O0OOOO00OOO0OOO00 ]#line:189
            elif id in OOO00OOO0OOOO00O0 ._points [O0OOOO00OOO0OOO00 ]:#line:190
                return OOO00OOO0OOOO00O0 ._points [O0OOOO00OOO0OOO00 ][id ]#line:191
        return None #line:192
    def get_box (O0O00O0O000OO00OO ,OOOO00O0O0O0O0OOO ,id ='all'):#line:194
        if isinstance (id ,str ):#line:195
            id =id .lower ()#line:196
            if id =='all':#line:197
                return O0O00O0O000OO00OO ._boxes [OOOO00O0O0O0O0OOO ]#line:198
            elif id in O0O00O0O000OO00OO ._boxes [OOOO00O0O0O0O0OOO ]:#line:199
                return O0O00O0O000OO00OO ._boxes [OOOO00O0O0O0O0OOO ][id ]#line:200
        return None #line:201
    def get_width (OOOO0000OOO00O0OO ,OO00OOOOO000OO00O ,id ='all'):#line:203
        if isinstance (id ,str ):#line:204
            id =id .lower ()#line:205
            if id =='all':#line:206
                return OOOO0000OOO00O0OO ._widths [OO00OOOOO000OO00O ]#line:207
            elif id in OOOO0000OOO00O0OO ._widths [OO00OOOOO000OO00O ]:#line:208
                return OOOO0000OOO00O0OO ._widths [OO00OOOOO000OO00O ][id ]#line:209
        return 0 #line:210
    def get_height (O0OOOOO0O000O000O ,O0O000OO0O0O000OO ,id ='all'):#line:212
        if isinstance (id ,str ):#line:213
            id =id .lower ()#line:214
            if id =='all':#line:215
                return O0OOOOO0O000O000O ._heights [O0O000OO0O0O000OO ]#line:216
            elif id in O0OOOOO0O000O000O ._heights [O0O000OO0O0O000OO ]:#line:217
                return O0OOOOO0O000O000O ._heights [O0O000OO0O0O000OO ][id ]#line:218
        return 0 #line:219
    def get_area (OO0000OO0000OO00O ,OOOO00OOOOOO00O0O ,id ='all'):#line:221
        if isinstance (id ,str ):#line:222
            id =id .lower ()#line:223
            if id =='all':#line:224
                return OO0000OO0000OO00O ._areas [OOOO00OOOOOO00O0O ]#line:225
            elif id in OO0000OO0000OO00O ._areas [OOOO00OOOOOO00O0O ]:#line:226
                return OO0000OO0000OO00O ._areas [OOOO00OOOOOO00O0O ][id ]#line:227
        return 0 #line:228
    def get_feature (OOOOO0OO0OOOOOO0O ,filter ='all'):#line:230
        OO0OOOOO0OOOOO00O =OOOOO0OO0OOOOOO0O .get_width ('left','palm')#line:231
        O00O000O000O000O0 =OOOOO0OO0OOOOOO0O .get_height ('left','palm')#line:232
        OOOOO0O0O00OOOO00 =[OO0OOOOO0OOOOO00O ,O00O000O000O000O0 ]#line:233
        if OO0OOOOO0OOOOO00O >0 and O00O000O000O000O0 >0 :#line:234
            OO0O0O000OO00OOO0 =OOOOO0OO0OOOOOO0O ._landmarks ['left']#line:235
            O0000OO00O000OOOO =OOOOO0OO0OOOOOO0O ._landmarks ['right']#line:236
            if OO0O0O000OO00OOO0 is not None and O0000OO00O000OOOO is not None :#line:237
                OO00O00OOO0OOO00O =OO0O0O000OO00OOO0 [0 ,:2 ]#line:238
                OO0O0O000OO00OOO0 =(OO0O0O000OO00OOO0 [1 :,:2 ]-OO00O00OOO0OOO00O )/OOOOO0O0O00OOOO00 #line:239
                OO00O00OOO0OOO00O =O0000OO00O000OOOO [0 ,:2 ]#line:240
                O0000OO00O000OOOO =(O0000OO00O000OOOO [1 :,:2 ]-OO00O00OOO0OOO00O )/OOOOO0O0O00OOOO00 #line:241
                O0OOOOOOO0OO000O0 =np .concatenate ((OO0O0O000OO00OOO0 .reshape (-1 ),O0000OO00O000OOOO .reshape (-1 )),axis =None )#line:242
                if isinstance (filter ,str ):#line:243
                    filter =filter .lower ()#line:244
                    if filter =='all':#line:245
                        return O0OOOOOOO0OO000O0 #line:246
                elif isinstance (filter ,(int ,float )):#line:247
                    filter =int (filter )#line:248
                    if filter >0 and filter <6 :#line:249
                        O0OO0OO000OO00OO0 =_O000OOOO0O0OO0O0O [filter -1 ]#line:250
                        return np .array ([O0OOOOOOO0OO000O0 [O00OO00OOO0O0000O ]for O00OO00OOO0O0000O in O0OO0OO000OO00OO0 ])#line:251
                elif isinstance (filter ,(list ,tuple )):#line:252
                    O0OO0OO000OO00OO0 =[]#line:253
                    for OO000O0OOO0O0000O in filter :#line:254
                        if isinstance (OO000O0OOO0O0000O ,(int ,float )):#line:255
                            OO000O0OOO0O0000O =int (OO000O0OOO0O0000O )#line:256
                            if OO000O0OOO0O0000O >0 and OO000O0OOO0O0000O <6 :#line:257
                                O0OO0OO000OO00OO0 .extend (_O000OOOO0O0OO0O0O [OO000O0OOO0O0000O -1 ])#line:258
                    return np .array ([O0OOOOOOO0OO000O0 [OO00OO0OO000000OO ]for OO00OO0OO000000OO in O0OO0OO000OO00OO0 ])#line:259
        return None #line:260
    def _get_feature_label (O0O0O0OO000O000O0 ,filter ='all'):#line:262
        if isinstance (filter ,str ):#line:263
            filter =filter .lower ()#line:264
            if filter =='all':#line:265
                return ['f'+str (O000000OOO00OO000 )for O000000OOO00OO000 in range (80 )]#line:266
        elif isinstance (filter ,(int ,float )):#line:267
            filter =int (filter )#line:268
            if filter >0 and filter <6 :#line:269
                OO000000OO000O00O =_O000OOOO0O0OO0O0O [filter -1 ]#line:270
                return ['f'+str (O0O0OO0000O00OO00 )for O0O0OO0000O00OO00 in OO000000OO000O00O ]#line:271
        elif isinstance (filter ,(list ,tuple )):#line:272
            OO000000OO000O00O =[]#line:273
            for OOOOOOOOO00O0OOO0 in filter :#line:274
                if isinstance (OOOOOOOOO00O0OOO0 ,(int ,float )):#line:275
                    OOOOOOOOO00O0OOO0 =int (OOOOOOOOO00O0OOO0 )#line:276
                    if OOOOOOOOO00O0OOO0 >0 and OOOOOOOOO00O0OOO0 <6 :#line:277
                        OO000000OO000O00O .extend (_O000OOOO0O0OO0O0O [OOOOOOOOO00O0OOO0 -1 ])#line:278
            return ['f'+str (O0O0OOO0000OO0000 )for O0O0OOO0000OO0000 in OO000000OO000O00O ]#line:279
    def record_feature (OO0OO0O00O00O000O ,O00OO00O00O00OO0O ,OOOOOO00O000OO000 ,filter ='all',interval_msec =100 ,frames =20 ,countdown =3 ):#line:281
        if countdown >0 :#line:282
            O00OO00O00O00OO0O .count_down (countdown )#line:283
        OOO000O0OOOO000O0 =0 #line:284
        O0O00O00OOOO00O00 =timer ()#line:285
        OO0000OO0OOOOO00O =','.join (OO0OO0O00O00O000O ._get_feature_label (filter ))#line:286
        O000OO0OOOO00O0O0 =[]#line:287
        while True :#line:288
            if OOO000O0OOOO000O0 >=frames :break #line:289
            O00000OO00000OOO0 =O00OO00O00O00OO0O .read ()#line:290
            if OO0OO0O00O00O000O .detect (O00000OO00000OOO0 ):#line:291
                O00000OO00000OOO0 =OO0OO0O00O00O000O .draw_result (O00000OO00000OOO0 )#line:292
                if timer ()>O0O00O00OOOO00O00 :#line:293
                    O000OO0OOOO00O0O0 .append (OO0OO0O00O00O000O .get_feature (filter ))#line:294
                    OOO000O0OOOO000O0 +=1 #line:295
                    print ('saved',OOO000O0OOOO000O0 )#line:296
                    O0O00O00OOOO00O00 +=interval_msec /1000.0 #line:297
                if O00OO00O00O00OO0O .check_key ()=='esc':#line:298
                    return #line:299
            O00OO00O00O00OO0O .show (O00000OO00000OOO0 )#line:300
        if OOOOOO00O000OO000 is not None :#line:301
            Util .realize_filepath (OOOOOO00O000OO000 )#line:302
            np .savetxt (OOOOOO00O000OO000 ,O000OO0OOOO00O0O0 ,fmt ='%f',delimiter =',',header =OO0000OO0OOOOO00O ,comments ='')#line:303
    @staticmethod #line:305
    def distance (OOOOOO0O0000O0OO0 ,O0O0O000000OO0OO0 ):#line:306
        return Util .distance (OOOOOO0O0000O0OO0 ,O0O0O000000OO0OO0 )#line:307
    @staticmethod #line:309
    def degree (O00O00O000OO0OOO0 ,O00000O0OOO0O0O00 ):#line:310
        return Util .degree (O00O00O000OO0OOO0 ,O00000O0OOO0O0O00 )#line:311
    @staticmethod #line:313
    def radian (O000OO0OOOO0O0OOO ,O0OOOO0O00O0O00OO ):#line:314
        return Util .radian (O000OO0OOOO0O0OOO ,O0OOOO0O00O0O00OO )#line:315
