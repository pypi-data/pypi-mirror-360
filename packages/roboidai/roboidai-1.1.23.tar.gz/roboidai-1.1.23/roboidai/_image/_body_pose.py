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
_O0OO000O0O0OOOO00 ={'head':[0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ],'left arm':[12 ,13 ,16 ,17 ,20 ,21 ,24 ,25 ],'right arm':[14 ,15 ,18 ,19 ,22 ,23 ,26 ,27 ],'left leg':[28 ,29 ,32 ,33 ,36 ,37 ,40 ,41 ],'right leg':[30 ,31 ,34 ,35 ,38 ,39 ,42 ,43 ]}#line:15
_OOOO00OO000OOO0O0 =[[11 ,12 ],[11 ,13 ],[13 ,15 ],[12 ,14 ],[14 ,16 ],[11 ,23 ],[12 ,24 ],[23 ,24 ],[23 ,25 ],[24 ,26 ],[25 ,27 ],[26 ,28 ]]#line:16
class BodyPose :#line:19
    def __init__ (O0O000OOOOO0OOOO0 ):#line:20
        O0O000OOOOO0OOOO0 ._loaded =False #line:21
        O0O000OOOOO0OOOO0 ._clear ()#line:22
    def _clear (OOOO00000O0O00O0O ):#line:24
        OOOO00000O0O00O0O ._landmarks =None #line:25
        OOOO00000O0O00O0O ._drawings =None #line:26
    def load_model (O00OO000OO000OOOO ,threshold =0.5 ):#line:28
        try :#line:29
            O00OO000OO000OOOO ._pose =mp .solutions .pose .Pose (min_detection_confidence =threshold ,min_tracking_confidence =0.5 )#line:30
            O00OO000OO000OOOO ._loaded =True #line:31
            return True #line:32
        except :#line:33
            return False #line:34
    def _fill_data (OOO00O0OOOOO0OO00 ,O0O0O0O000000O0OO ):#line:36
        O000O00000O000OOO ={}#line:37
        O000O00000O000OOO ['left eye']=O0O0O0O000000O0OO [5 ]#line:38
        O000O00000O000OOO ['right eye']=O0O0O0O000000O0OO [2 ]#line:39
        O000O00000O000OOO ['left ear']=O0O0O0O000000O0OO [8 ]#line:40
        O000O00000O000OOO ['right ear']=O0O0O0O000000O0OO [7 ]#line:41
        O000O00000O000OOO ['nose']=O0O0O0O000000O0OO [0 ]#line:42
        O000O00000O000OOO ['mouth']=np .around (O0O0O0O000000O0OO [9 ]*0.5 +O0O0O0O000000O0OO [10 ]*0.5 ).astype (np .int32 )#line:43
        OO0O00OOOO00OO0O0 =O0O0O0O000000O0OO [11 ]*0.5 +O0O0O0O000000O0OO [12 ]*0.5 #line:44
        OO0O00OOOO00OO0O0 [0 ]=OO0O00OOOO00OO0O0 [0 ]*0.5 +O0O0O0O000000O0OO [0 ][0 ]*0.5 #line:45
        OO0O00OOOO00OO0O0 [1 ]=OO0O00OOOO00OO0O0 [1 ]*0.75 +O0O0O0O000000O0OO [0 ][1 ]*0.25 #line:46
        O000O00000O000OOO ['neck']=np .around (OO0O00OOOO00OO0O0 ).astype (np .int32 )#line:47
        O000O00000O000OOO ['left shoulder']=O0O0O0O000000O0OO [12 ]#line:48
        O000O00000O000OOO ['right shoulder']=O0O0O0O000000O0OO [11 ]#line:49
        O000O00000O000OOO ['left elbow']=O0O0O0O000000O0OO [14 ]#line:50
        O000O00000O000OOO ['right elbow']=O0O0O0O000000O0OO [13 ]#line:51
        O000O00000O000OOO ['left wrist']=O0O0O0O000000O0OO [16 ]#line:52
        O000O00000O000OOO ['right wrist']=O0O0O0O000000O0OO [15 ]#line:53
        O000O00000O000OOO ['left hand']=np .around ((O0O0O0O000000O0OO [16 ]+O0O0O0O000000O0OO [18 ]+O0O0O0O000000O0OO [20 ]+O0O0O0O000000O0OO [22 ])*0.25 ).astype (np .int32 )#line:54
        O000O00000O000OOO ['right hand']=np .around ((O0O0O0O000000O0OO [15 ]+O0O0O0O000000O0OO [17 ]+O0O0O0O000000O0OO [19 ]+O0O0O0O000000O0OO [21 ])*0.25 ).astype (np .int32 )#line:55
        O000O00000O000OOO ['left hip']=O0O0O0O000000O0OO [24 ]#line:56
        O000O00000O000OOO ['right hip']=O0O0O0O000000O0OO [23 ]#line:57
        O000O00000O000OOO ['left knee']=O0O0O0O000000O0OO [26 ]#line:58
        O000O00000O000OOO ['right knee']=O0O0O0O000000O0OO [25 ]#line:59
        O000O00000O000OOO ['left ankle']=O0O0O0O000000O0OO [28 ]#line:60
        O000O00000O000OOO ['right ankle']=O0O0O0O000000O0OO [27 ]#line:61
        O000O00000O000OOO ['left foot']=np .around ((O0O0O0O000000O0OO [28 ]+O0O0O0O000000O0OO [30 ]+O0O0O0O000000O0OO [32 ])/3 ).astype (np .int32 )#line:62
        O000O00000O000OOO ['right foot']=np .around ((O0O0O0O000000O0OO [27 ]+O0O0O0O000000O0OO [29 ]+O0O0O0O000000O0OO [31 ])/3 ).astype (np .int32 )#line:63
        return O000O00000O000OOO #line:64
    def detect (O00O00O0O00O00O0O ,O0O00OOO000O0O0O0 ):#line:66
        if O0O00OOO000O0O0O0 is not None and O00O00O0O00O00O0O ._loaded :#line:67
            O0O00OOO000O0O0O0 =cv2 .cvtColor (O0O00OOO000O0O0O0 ,cv2 .COLOR_BGR2RGB )#line:68
            O0O00OOO000O0O0O0 .flags .writeable =False #line:69
            O000000O0OOO000O0 =O00O00O0O00O00O0O ._pose .process (O0O00OOO000O0O0O0 )#line:70
            if O000000O0OOO000O0 and O000000O0OOO000O0 .pose_landmarks :#line:71
                OOO000OO00OO0000O =O000000O0OOO000O0 .pose_landmarks #line:72
                OOOO0000O0OO00O0O =O0O00OOO000O0O0O0 .shape [1 ]#line:73
                OOO0OO0O000OO00OO =O0O00OOO000O0O0O0 .shape [0 ]#line:74
                OOO00OO0OOOOO0OO0 =[O0OO0OOO00OOO00OO .x for O0OO0OOO00OOO00OO in OOO000OO00OO0000O .landmark ]#line:75
                O0OOO0OOO0OO00O0O =[OOOOO0O0000OO0OOO .y for OOOOO0O0000OO0OOO in OOO000OO00OO0000O .landmark ]#line:76
                OOO00000O00000O0O =np .transpose (np .stack ((OOO00OO0OOOOO0OO0 ,O0OOO0OOO0OO00O0O )))*(OOOO0000O0OO00O0O ,OOO0OO0O000OO00OO )#line:77
                OOO00000O00000O0O =OOO00000O00000O0O .astype (np .int32 )#line:78
                O00O00O0O00O00O0O ._landmarks =O00O00O0O00O00O0O ._fill_data (OOO00000O00000O0O )#line:79
                O00O00O0O00O00O0O ._drawings =[OOO00000O00000O0O ,O00O00O0O00O00O0O ._landmarks ]#line:80
                return True #line:81
        O00O00O0O00O00O0O ._clear ()#line:82
        return False #line:83
    def draw_result (O00000O000O0O0000 ,O0000OO00O0000O0O ,clone =False ):#line:85
        if O0000OO00O0000O0O is not None and O00000O000O0O0000 ._drawings is not None :#line:86
            if clone :#line:87
                O0000OO00O0000O0O =O0000OO00O0000O0O .copy ()#line:88
            O0OO00O000OOO0O0O =O00000O000O0O0000 ._drawings #line:89
            OO00OOOOOOO00000O =O0OO00O000OOO0O0O [0 ]#line:90
            for O00OO000O0000OO0O in _OOOO00OO000OOO0O0 :#line:91
                O0OO0O0OOO0O0O0O0 =OO00OOOOOOO00000O [O00OO000O0000OO0O [0 ]]#line:92
                O00OO00O000OO000O =OO00OOOOOOO00000O [O00OO000O0000OO0O [1 ]]#line:93
                cv2 .line (O0000OO00O0000O0O ,(O0OO0O0OOO0O0O0O0 [0 ],O0OO0O0OOO0O0O0O0 [1 ]),(O00OO00O000OO000O [0 ],O00OO00O000OO000O [1 ]),(0 ,255 ,0 ),3 )#line:94
            O0000OO0O0OOO00OO =O0OO00O000OOO0O0O [1 ]#line:95
            for OO000O00OOO0O0OOO in O0000OO0O0OOO00OO :#line:96
                OOOO0OO0OO00000OO =O0000OO0O0OOO00OO [OO000O00OOO0O0OOO ]#line:97
                cv2 .circle (O0000OO00O0000O0O ,(OOOO0OO0OO00000OO [0 ],OOOO0OO0OO00000OO [1 ]),3 ,(0 ,0 ,255 ),2 )#line:98
        return O0000OO00O0000O0O #line:99
    def get_xy (O000O00O0OO0OO0O0 ,id ='all'):#line:101
        if isinstance (id ,str ):#line:102
            OO00O0OOO00OO0O00 =O000O00O0OO0OO0O0 ._landmarks #line:103
            id =id .lower ()#line:104
            if id =='all':#line:105
                return OO00O0OOO00OO0O00 #line:106
            elif OO00O0OOO00OO0O00 is None :#line:107
                return None #line:108
            elif id in OO00O0OOO00OO0O00 :#line:109
                return OO00O0OOO00OO0O00 [id ]#line:110
        return None #line:111
    def get_feature (O00O0OO000OOO0OO0 ,filter ='all'):#line:113
        O0OO0OOO0O0O0O0O0 =O00O0OO000OOO0OO0 ._landmarks #line:114
        if O0OO0OOO0O0O0O0O0 is not None :#line:115
            O0000O0OOO00OOO0O =abs (O0OO0OOO0O0O0O0O0 ['right shoulder'][0 ]-O0OO0OOO0O0O0O0O0 ['left shoulder'][0 ])#line:116
            if O0000O0OOO00OOO0O >0 :#line:117
                OOOO00O000O0OO000 =[]#line:118
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left eye'])#line:119
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right eye'])#line:120
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left ear'])#line:121
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right ear'])#line:122
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['nose'])#line:123
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['mouth'])#line:124
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left shoulder'])#line:125
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right shoulder'])#line:126
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left elbow'])#line:127
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right elbow'])#line:128
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left wrist'])#line:129
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right wrist'])#line:130
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left hand'])#line:131
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right hand'])#line:132
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left hip'])#line:133
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right hip'])#line:134
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left knee'])#line:135
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right knee'])#line:136
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left ankle'])#line:137
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right ankle'])#line:138
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['left foot'])#line:139
                OOOO00O000O0OO000 .append (O0OO0OOO0O0O0O0O0 ['right foot'])#line:140
                OO00OO0O0O0O0OOO0 =O0OO0OOO0O0O0O0O0 ['neck']#line:142
                OOOO00O000O0OO000 =(OOOO00O000O0OO000 -OO00OO0O0O0O0OOO0 )/O0000O0OOO00OOO0O #line:143
                OOOO00O000O0OO000 =OOOO00O000O0OO000 .reshape (-1 )#line:144
                if isinstance (filter ,str ):#line:146
                    filter =filter .lower ()#line:147
                    if filter =='all':#line:148
                        return OOOO00O000O0OO000 #line:149
                    elif filter in _O0OO000O0O0OOOO00 :#line:150
                        O00O0000OOO00O00O =_O0OO000O0O0OOOO00 [filter ]#line:151
                        return np .array ([OOOO00O000O0OO000 [O00O00O0OO00O00O0 ]for O00O00O0OO00O00O0 in O00O0000OOO00O00O ])#line:152
                elif isinstance (filter ,(list ,tuple )):#line:153
                    O00O0000OOO00O00O =[]#line:154
                    for O0O000O00O0000O0O in filter :#line:155
                        if O0O000O00O0000O0O in _O0OO000O0O0OOOO00 :#line:156
                            O00O0000OOO00O00O .extend (_O0OO000O0O0OOOO00 [O0O000O00O0000O0O ])#line:157
                    return np .array ([OOOO00O000O0OO000 [OOO00O0OOOOO000OO ]for OOO00O0OOOOO000OO in O00O0000OOO00O00O ])#line:158
        return None #line:159
    def _get_feature_label (O0000000OO0OOOOOO ,filter ='all'):#line:161
        if isinstance (filter ,str ):#line:162
            filter =filter .lower ()#line:163
            if filter =='all':#line:164
                return ['f'+str (OO0O0OOOOO0OO0O00 )for OO0O0OOOOO0OO0O00 in range (44 )]#line:165
            elif filter in _O0OO000O0O0OOOO00 :#line:166
                OOO00OO0OO00O0000 =_O0OO000O0O0OOOO00 [filter ]#line:167
                return ['f'+str (OOO000000O00OOOO0 )for OOO000000O00OOOO0 in OOO00OO0OO00O0000 ]#line:168
        elif isinstance (filter ,(list ,tuple )):#line:169
            OOO00OO0OO00O0000 =[]#line:170
            for O0O00O00O00O000O0 in filter :#line:171
                if O0O00O00O00O000O0 in _O0OO000O0O0OOOO00 :#line:172
                    OOO00OO0OO00O0000 .extend (_O0OO000O0O0OOOO00 [O0O00O00O00O000O0 ])#line:173
            return ['f'+str (OO0O0O0OOO0OO0O00 )for OO0O0O0OOO0OO0O00 in OOO00OO0OO00O0000 ]#line:174
    def record_feature (OOO0O00O00OO0OOOO ,OOO0000O0O0000OOO ,OO0O0O000OO0OO00O ,filter ='all',interval_msec =100 ,frames =20 ,countdown =3 ):#line:176
        if countdown >0 :#line:177
            OOO0000O0O0000OOO .count_down (countdown )#line:178
        O00OOOOO0OOOOO00O =0 #line:179
        OO0O000OO000OO00O =timer ()#line:180
        O0O0000O00O000OOO =','.join (OOO0O00O00OO0OOOO ._get_feature_label (filter ))#line:181
        OO0O000OO00OOOO00 =[]#line:182
        while True :#line:183
            if O00OOOOO0OOOOO00O >=frames :break #line:184
            O00OOO000OOO0OOOO =OOO0000O0O0000OOO .read ()#line:185
            if OOO0O00O00OO0OOOO .detect (O00OOO000OOO0OOOO ):#line:186
                O00OOO000OOO0OOOO =OOO0O00O00OO0OOOO .draw_result (O00OOO000OOO0OOOO )#line:187
                if timer ()>OO0O000OO000OO00O :#line:188
                    OO0O000OO00OOOO00 .append (OOO0O00O00OO0OOOO .get_feature (filter ))#line:189
                    O00OOOOO0OOOOO00O +=1 #line:190
                    print ('saved',O00OOOOO0OOOOO00O )#line:191
                    OO0O000OO000OO00O +=interval_msec /1000.0 #line:192
                if OOO0000O0O0000OOO .check_key ()=='esc':#line:193
                    return #line:194
            OOO0000O0O0000OOO .show (O00OOO000OOO0OOOO )#line:195
        if OO0O0O000OO0OO00O is not None :#line:196
            Util .realize_filepath (OO0O0O000OO0OO00O )#line:197
            np .savetxt (OO0O0O000OO0OO00O ,OO0O000OO00OOOO00 ,fmt ='%f',delimiter =',',header =O0O0000O00O000OOO ,comments ='')#line:198
    @staticmethod #line:200
    def distance (O000OOO00O0OO0000 ,O0OOO0OOO0O0O0OOO ):#line:201
        return Util .distance (O000OOO00O0OO0000 ,O0OOO0OOO0O0O0OOO )#line:202
    @staticmethod #line:204
    def degree (O00OO00000OO0OO00 ,OO000OOO0O0OO000O ):#line:205
        return Util .degree (O00OO00000OO0OO00 ,OO000OOO0O0OO000O )#line:206
    @staticmethod #line:208
    def radian (OOO0OO000O00OOOO0 ,OOO00OOOOOOOO0O0O ):#line:209
        return Util .radian (OOO0OO000O00OOOO0 ,OOO00OOOOOOOO0O0O )#line:210
