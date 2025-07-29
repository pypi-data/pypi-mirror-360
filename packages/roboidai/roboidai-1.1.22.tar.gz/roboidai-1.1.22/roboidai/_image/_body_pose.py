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
_O0O00O00O0OOO00OO ={'head':[0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ],'left arm':[12 ,13 ,16 ,17 ,20 ,21 ,24 ,25 ],'right arm':[14 ,15 ,18 ,19 ,22 ,23 ,26 ,27 ],'left leg':[28 ,29 ,32 ,33 ,36 ,37 ,40 ,41 ],'right leg':[30 ,31 ,34 ,35 ,38 ,39 ,42 ,43 ]}#line:15
_O000O0O0000O0OO00 =[[11 ,12 ],[11 ,13 ],[13 ,15 ],[12 ,14 ],[14 ,16 ],[11 ,23 ],[12 ,24 ],[23 ,24 ],[23 ,25 ],[24 ,26 ],[25 ,27 ],[26 ,28 ]]#line:16
class BodyPose :#line:19
    def __init__ (O0O0OOO0O0O0O0OO0 ):#line:20
        O0O0OOO0O0O0O0OO0 ._loaded =False #line:21
        O0O0OOO0O0O0O0OO0 ._clear ()#line:22
    def _clear (O00O0OOO00O0OO0O0 ):#line:24
        O00O0OOO00O0OO0O0 ._landmarks =None #line:25
        O00O0OOO00O0OO0O0 ._drawings =None #line:26
    def load_model (O00O00O0OO0OO0OO0 ,threshold =0.5 ):#line:28
        try :#line:29
            O00O00O0OO0OO0OO0 ._pose =mp .solutions .pose .Pose (min_detection_confidence =threshold ,min_tracking_confidence =0.5 )#line:30
            O00O00O0OO0OO0OO0 ._loaded =True #line:31
            return True #line:32
        except :#line:33
            return False #line:34
    def _fill_data (O00O0O0O000O0000O ,O00O0OO0000OO0O00 ):#line:36
        OO0OO0O00O0000O0O ={}#line:37
        OO0OO0O00O0000O0O ['left eye']=O00O0OO0000OO0O00 [5 ]#line:38
        OO0OO0O00O0000O0O ['right eye']=O00O0OO0000OO0O00 [2 ]#line:39
        OO0OO0O00O0000O0O ['left ear']=O00O0OO0000OO0O00 [8 ]#line:40
        OO0OO0O00O0000O0O ['right ear']=O00O0OO0000OO0O00 [7 ]#line:41
        OO0OO0O00O0000O0O ['nose']=O00O0OO0000OO0O00 [0 ]#line:42
        OO0OO0O00O0000O0O ['mouth']=np .around (O00O0OO0000OO0O00 [9 ]*0.5 +O00O0OO0000OO0O00 [10 ]*0.5 ).astype (np .int32 )#line:43
        O0O0OOO00O0O0OO0O =O00O0OO0000OO0O00 [11 ]*0.5 +O00O0OO0000OO0O00 [12 ]*0.5 #line:44
        O0O0OOO00O0O0OO0O [0 ]=O0O0OOO00O0O0OO0O [0 ]*0.5 +O00O0OO0000OO0O00 [0 ][0 ]*0.5 #line:45
        O0O0OOO00O0O0OO0O [1 ]=O0O0OOO00O0O0OO0O [1 ]*0.75 +O00O0OO0000OO0O00 [0 ][1 ]*0.25 #line:46
        OO0OO0O00O0000O0O ['neck']=np .around (O0O0OOO00O0O0OO0O ).astype (np .int32 )#line:47
        OO0OO0O00O0000O0O ['left shoulder']=O00O0OO0000OO0O00 [12 ]#line:48
        OO0OO0O00O0000O0O ['right shoulder']=O00O0OO0000OO0O00 [11 ]#line:49
        OO0OO0O00O0000O0O ['left elbow']=O00O0OO0000OO0O00 [14 ]#line:50
        OO0OO0O00O0000O0O ['right elbow']=O00O0OO0000OO0O00 [13 ]#line:51
        OO0OO0O00O0000O0O ['left wrist']=O00O0OO0000OO0O00 [16 ]#line:52
        OO0OO0O00O0000O0O ['right wrist']=O00O0OO0000OO0O00 [15 ]#line:53
        OO0OO0O00O0000O0O ['left hand']=np .around ((O00O0OO0000OO0O00 [16 ]+O00O0OO0000OO0O00 [18 ]+O00O0OO0000OO0O00 [20 ]+O00O0OO0000OO0O00 [22 ])*0.25 ).astype (np .int32 )#line:54
        OO0OO0O00O0000O0O ['right hand']=np .around ((O00O0OO0000OO0O00 [15 ]+O00O0OO0000OO0O00 [17 ]+O00O0OO0000OO0O00 [19 ]+O00O0OO0000OO0O00 [21 ])*0.25 ).astype (np .int32 )#line:55
        OO0OO0O00O0000O0O ['left hip']=O00O0OO0000OO0O00 [24 ]#line:56
        OO0OO0O00O0000O0O ['right hip']=O00O0OO0000OO0O00 [23 ]#line:57
        OO0OO0O00O0000O0O ['left knee']=O00O0OO0000OO0O00 [26 ]#line:58
        OO0OO0O00O0000O0O ['right knee']=O00O0OO0000OO0O00 [25 ]#line:59
        OO0OO0O00O0000O0O ['left ankle']=O00O0OO0000OO0O00 [28 ]#line:60
        OO0OO0O00O0000O0O ['right ankle']=O00O0OO0000OO0O00 [27 ]#line:61
        OO0OO0O00O0000O0O ['left foot']=np .around ((O00O0OO0000OO0O00 [28 ]+O00O0OO0000OO0O00 [30 ]+O00O0OO0000OO0O00 [32 ])/3 ).astype (np .int32 )#line:62
        OO0OO0O00O0000O0O ['right foot']=np .around ((O00O0OO0000OO0O00 [27 ]+O00O0OO0000OO0O00 [29 ]+O00O0OO0000OO0O00 [31 ])/3 ).astype (np .int32 )#line:63
        return OO0OO0O00O0000O0O #line:64
    def detect (OOOOOOOOO000OO00O ,OO00OOOO000O00O0O ):#line:66
        if OO00OOOO000O00O0O is not None and OOOOOOOOO000OO00O ._loaded :#line:67
            OO00OOOO000O00O0O =cv2 .cvtColor (OO00OOOO000O00O0O ,cv2 .COLOR_BGR2RGB )#line:68
            OO00OOOO000O00O0O .flags .writeable =False #line:69
            O00000OO0000OO000 =OOOOOOOOO000OO00O ._pose .process (OO00OOOO000O00O0O )#line:70
            if O00000OO0000OO000 and O00000OO0000OO000 .pose_landmarks :#line:71
                O0OO000OO0O000OOO =O00000OO0000OO000 .pose_landmarks #line:72
                OO0OO0O0OOO00000O =OO00OOOO000O00O0O .shape [1 ]#line:73
                OO000O0OO00O000O0 =OO00OOOO000O00O0O .shape [0 ]#line:74
                OO0O0OO0OO0OOOO00 =[O00OO00O0000O00O0 .x for O00OO00O0000O00O0 in O0OO000OO0O000OOO .landmark ]#line:75
                O0O0000OOOO0O00O0 =[OO000O0OOOOOOO00O .y for OO000O0OOOOOOO00O in O0OO000OO0O000OOO .landmark ]#line:76
                O00O00O0OOOOO0O0O =np .transpose (np .stack ((OO0O0OO0OO0OOOO00 ,O0O0000OOOO0O00O0 )))*(OO0OO0O0OOO00000O ,OO000O0OO00O000O0 )#line:77
                O00O00O0OOOOO0O0O =O00O00O0OOOOO0O0O .astype (np .int32 )#line:78
                OOOOOOOOO000OO00O ._landmarks =OOOOOOOOO000OO00O ._fill_data (O00O00O0OOOOO0O0O )#line:79
                OOOOOOOOO000OO00O ._drawings =[O00O00O0OOOOO0O0O ,OOOOOOOOO000OO00O ._landmarks ]#line:80
                return True #line:81
        OOOOOOOOO000OO00O ._clear ()#line:82
        return False #line:83
    def draw_result (OO0OO0O00O00OOOOO ,O0O0OOO0000OOOO00 ,clone =False ):#line:85
        if O0O0OOO0000OOOO00 is not None and OO0OO0O00O00OOOOO ._drawings is not None :#line:86
            if clone :#line:87
                O0O0OOO0000OOOO00 =O0O0OOO0000OOOO00 .copy ()#line:88
            OOO0OOOOOOOOOO00O =OO0OO0O00O00OOOOO ._drawings #line:89
            OO0O0O0O000O0O000 =OOO0OOOOOOOOOO00O [0 ]#line:90
            for O0O00OO00000OOOOO in _O000O0O0000O0OO00 :#line:91
                O0OO000O0OOO00000 =OO0O0O0O000O0O000 [O0O00OO00000OOOOO [0 ]]#line:92
                OOOOO0O000OOOOOO0 =OO0O0O0O000O0O000 [O0O00OO00000OOOOO [1 ]]#line:93
                cv2 .line (O0O0OOO0000OOOO00 ,(O0OO000O0OOO00000 [0 ],O0OO000O0OOO00000 [1 ]),(OOOOO0O000OOOOOO0 [0 ],OOOOO0O000OOOOOO0 [1 ]),(0 ,255 ,0 ),3 )#line:94
            OOO000OO0OOO000OO =OOO0OOOOOOOOOO00O [1 ]#line:95
            for O0O0O0O0OOOO000OO in OOO000OO0OOO000OO :#line:96
                O00OO00O00O0O0O00 =OOO000OO0OOO000OO [O0O0O0O0OOOO000OO ]#line:97
                cv2 .circle (O0O0OOO0000OOOO00 ,(O00OO00O00O0O0O00 [0 ],O00OO00O00O0O0O00 [1 ]),3 ,(0 ,0 ,255 ),2 )#line:98
        return O0O0OOO0000OOOO00 #line:99
    def get_xy (OOO0OOOOOO00O00OO ,id ='all'):#line:101
        if isinstance (id ,str ):#line:102
            O0OO0O00OO000O0OO =OOO0OOOOOO00O00OO ._landmarks #line:103
            id =id .lower ()#line:104
            if id =='all':#line:105
                return O0OO0O00OO000O0OO #line:106
            elif O0OO0O00OO000O0OO is None :#line:107
                return None #line:108
            elif id in O0OO0O00OO000O0OO :#line:109
                return O0OO0O00OO000O0OO [id ]#line:110
        return None #line:111
    def get_feature (OO00O00O0OO0OO0OO ,filter ='all'):#line:113
        O000O00OO0000O0OO =OO00O00O0OO0OO0OO ._landmarks #line:114
        if O000O00OO0000O0OO is not None :#line:115
            O0O00OOOOO0000OO0 =abs (O000O00OO0000O0OO ['right shoulder'][0 ]-O000O00OO0000O0OO ['left shoulder'][0 ])#line:116
            if O0O00OOOOO0000OO0 >0 :#line:117
                OOO000OOO0OO0O000 =[]#line:118
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left eye'])#line:119
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right eye'])#line:120
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left ear'])#line:121
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right ear'])#line:122
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['nose'])#line:123
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['mouth'])#line:124
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left shoulder'])#line:125
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right shoulder'])#line:126
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left elbow'])#line:127
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right elbow'])#line:128
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left wrist'])#line:129
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right wrist'])#line:130
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left hand'])#line:131
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right hand'])#line:132
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left hip'])#line:133
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right hip'])#line:134
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left knee'])#line:135
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right knee'])#line:136
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left ankle'])#line:137
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right ankle'])#line:138
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['left foot'])#line:139
                OOO000OOO0OO0O000 .append (O000O00OO0000O0OO ['right foot'])#line:140
                O0O0O0000OO00OOOO =O000O00OO0000O0OO ['neck']#line:142
                OOO000OOO0OO0O000 =(OOO000OOO0OO0O000 -O0O0O0000OO00OOOO )/O0O00OOOOO0000OO0 #line:143
                OOO000OOO0OO0O000 =OOO000OOO0OO0O000 .reshape (-1 )#line:144
                if isinstance (filter ,str ):#line:146
                    filter =filter .lower ()#line:147
                    if filter =='all':#line:148
                        return OOO000OOO0OO0O000 #line:149
                    elif filter in _O0O00O00O0OOO00OO :#line:150
                        O000O0OOO0OOOOOO0 =_O0O00O00O0OOO00OO [filter ]#line:151
                        return np .array ([OOO000OOO0OO0O000 [OO00O0O0O0OO000O0 ]for OO00O0O0O0OO000O0 in O000O0OOO0OOOOOO0 ])#line:152
                elif isinstance (filter ,(list ,tuple )):#line:153
                    O000O0OOO0OOOOOO0 =[]#line:154
                    for O0OOOOOO00OOOOOO0 in filter :#line:155
                        if O0OOOOOO00OOOOOO0 in _O0O00O00O0OOO00OO :#line:156
                            O000O0OOO0OOOOOO0 .extend (_O0O00O00O0OOO00OO [O0OOOOOO00OOOOOO0 ])#line:157
                    return np .array ([OOO000OOO0OO0O000 [OO0OOOOO000OO0O0O ]for OO0OOOOO000OO0O0O in O000O0OOO0OOOOOO0 ])#line:158
        return None #line:159
    def _get_feature_label (O0OO000000OO0O0O0 ,filter ='all'):#line:161
        if isinstance (filter ,str ):#line:162
            filter =filter .lower ()#line:163
            if filter =='all':#line:164
                return ['f'+str (O00OOO0000OO00O0O )for O00OOO0000OO00O0O in range (44 )]#line:165
            elif filter in _O0O00O00O0OOO00OO :#line:166
                O0000OO0OO0OO0O0O =_O0O00O00O0OOO00OO [filter ]#line:167
                return ['f'+str (OOO0OOO00O0O00OOO )for OOO0OOO00O0O00OOO in O0000OO0OO0OO0O0O ]#line:168
        elif isinstance (filter ,(list ,tuple )):#line:169
            O0000OO0OO0OO0O0O =[]#line:170
            for O0OOO0O0OOO00OO0O in filter :#line:171
                if O0OOO0O0OOO00OO0O in _O0O00O00O0OOO00OO :#line:172
                    O0000OO0OO0OO0O0O .extend (_O0O00O00O0OOO00OO [O0OOO0O0OOO00OO0O ])#line:173
            return ['f'+str (OOOOO00O00O0OOOO0 )for OOOOO00O00O0OOOO0 in O0000OO0OO0OO0O0O ]#line:174
    def record_feature (O0OOOO00OO0OO0O0O ,OO000OOO000OO000O ,OOO0OOOO00OO0OO00 ,filter ='all',interval_msec =100 ,frames =20 ,countdown =3 ):#line:176
        if countdown >0 :#line:177
            OO000OOO000OO000O .count_down (countdown )#line:178
        OO0OO000O0O0OOO0O =0 #line:179
        O0O00OO0O0OO0O0O0 =timer ()#line:180
        O0O0OO0OOOOO000O0 =','.join (O0OOOO00OO0OO0O0O ._get_feature_label (filter ))#line:181
        OOO00OO00O00OO00O =[]#line:182
        while True :#line:183
            if OO0OO000O0O0OOO0O >=frames :break #line:184
            OOOO000O000000OO0 =OO000OOO000OO000O .read ()#line:185
            if O0OOOO00OO0OO0O0O .detect (OOOO000O000000OO0 ):#line:186
                OOOO000O000000OO0 =O0OOOO00OO0OO0O0O .draw_result (OOOO000O000000OO0 )#line:187
                if timer ()>O0O00OO0O0OO0O0O0 :#line:188
                    OOO00OO00O00OO00O .append (O0OOOO00OO0OO0O0O .get_feature (filter ))#line:189
                    OO0OO000O0O0OOO0O +=1 #line:190
                    print ('saved',OO0OO000O0O0OOO0O )#line:191
                    O0O00OO0O0OO0O0O0 +=interval_msec /1000.0 #line:192
                if OO000OOO000OO000O .check_key ()=='esc':#line:193
                    return #line:194
            OO000OOO000OO000O .show (OOOO000O000000OO0 )#line:195
        if OOO0OOOO00OO0OO00 is not None :#line:196
            Util .realize_filepath (OOO0OOOO00OO0OO00 )#line:197
            np .savetxt (OOO0OOOO00OO0OO00 ,OOO00OO00O00OO00O ,fmt ='%f',delimiter =',',header =O0O0OO0OOOOO000O0 ,comments ='')#line:198
    @staticmethod #line:200
    def distance (O0OOOO0OOOO000OO0 ,OO0O00O0OOOO00OOO ):#line:201
        return Util .distance (O0OOOO0OOOO000OO0 ,OO0O00O0OOOO00OOO )#line:202
    @staticmethod #line:204
    def degree (OO000O0OO0O0OOOO0 ,OOO000OOOO00OO00O ):#line:205
        return Util .degree (OO000O0OO0O0OOOO0 ,OOO000OOOO00OO00O )#line:206
    @staticmethod #line:208
    def radian (OO0OOOOOOO00OOO00 ,O0O0OO0OOOOOOO000 ):#line:209
        return Util .radian (OO0OOOOOOO00OOO00 ,O0O0OO0OOOOOOO000 )#line:210
