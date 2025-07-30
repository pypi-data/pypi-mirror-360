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

import numpy as np #line:2
import matplotlib .pyplot as plt #line:3
from sklearn .linear_model import LinearRegression as Regression #line:4
class LinearRegression :#line:7
    def __init__ (OOOOOOO0OOOO0OOO0 ):#line:8
        OOOOOOO0OOOO0OOO0 ._regression =Regression ()#line:9
        OOOOOOO0OOOO0OOO0 ._clear ()#line:10
    def _clear (O0OOOOOOOOOO00O00 ):#line:12
        O0OOOOOOOOOO00O00 ._labels =None #line:13
        O0OOOOOOOOOO00O00 ._data =None #line:14
        O0OOOOOOOOOO00O00 ._columns ={}#line:15
        O0OOOOOOOOOO00O00 ._clear_result ()#line:16
    def _clear_result (O000OO0OOOO0O0O0O ):#line:18
        O000OO0OOOO0O0O0O ._result ={'xlabels':None ,'ylabels':None ,'weights':{}}#line:23
    def _to_label (OOOO000O00OOOOO00 ,O0OO0OO00O00OO0O0 ):#line:25
        if OOOO000O00OOOOO00 ._labels is not None :#line:26
            if isinstance (O0OO0OO00O00OO0O0 ,(int ,float )):#line:27
                O0OO0OO00O00OO0O0 =int (O0OO0OO00O00OO0O0 )#line:28
                if O0OO0OO00O00OO0O0 >=0 and O0OO0OO00O00OO0O0 <len (OOOO000O00OOOOO00 ._labels ):#line:29
                    return OOOO000O00OOOOO00 ._labels [O0OO0OO00O00OO0O0 ]#line:30
            elif isinstance (O0OO0OO00O00OO0O0 ,str ):#line:31
                if O0OO0OO00O00OO0O0 in OOOO000O00OOOOO00 ._labels :#line:32
                    return O0OO0OO00O00OO0O0 #line:33
        return None #line:34
    def load_data (O00O0O0OO0OOO0OOO ,O0O00000OOOOO00OO ):#line:36
        O00O0O0OO0OOO0OOO ._clear ()#line:37
        O00O0O0OO0OOO0OOO ._labels =np .loadtxt (O0O00000OOOOO00OO ,dtype ='str',delimiter =',',max_rows =1 )#line:38
        O00O0O0OO0OOO0OOO ._data =np .loadtxt (O0O00000OOOOO00OO ,delimiter =',',skiprows =1 )#line:39
        for O000OO00OO0O00000 ,OO0OOO0000OOO0OOO in enumerate (O00O0O0OO0OOO0OOO ._labels ):#line:40
            O00O0O0OO0OOO0OOO ._columns [OO0OOO0000OOO0OOO ]=O00O0O0OO0OOO0OOO ._data [:,O000OO00OO0O00000 ]#line:41
        return O00O0O0OO0OOO0OOO ._data #line:42
    def get_label (O00O00OOO00OO0000 ,index ='all'):#line:44
        if O00O00OOO00OO0000 ._labels is not None :#line:45
            if isinstance (index ,(int ,float )):#line:46
                index =int (index )#line:47
                if index >=0 and index <len (O00O00OOO00OO0000 ._labels ):#line:48
                    return O00O00OOO00OO0000 ._labels [index ]#line:49
            elif isinstance (index ,str ):#line:50
                if index .lower ()=='all':#line:51
                    return O00O00OOO00OO0000 ._labels #line:52
        return None #line:53
    def _get_data (O000OOOO00000OOO0 ,OOO0OOO00OO000OOO ):#line:55
        if OOO0OOO00OO000OOO is not None and OOO0OOO00OO000OOO in O000OOOO00000OOO0 ._columns :#line:56
            return O000OOOO00000OOO0 ._columns [OOO0OOO00OO000OOO ]#line:57
        return None #line:58
    def get_data (O000OO00OOOO0OO0O ,label ='all'):#line:60
        if isinstance (label ,str )and label .lower ()=='all':#line:61
            return O000OO00OOOO0OO0O ._data #line:62
        label =O000OO00OOOO0OO0O ._to_label (label )#line:63
        return O000OO00OOOO0OO0O ._get_data (label )#line:64
    def fit (OO000OO00OOOO0O00 ,O0OO00OOO00O0OO0O ,O00OOO000OOOO0OOO ):#line:66
        OO000OO00OOOO0O00 ._clear_result ()#line:67
        if not isinstance (O0OO00OOO00O0OO0O ,(list ,tuple )):#line:68
            O0OO00OOO00O0OO0O =(O0OO00OOO00O0OO0O ,)#line:69
        O0OO00OOO00O0OO0O =[OO000OO00OOOO0O00 ._to_label (O0OOO000OO0OO0O0O )for O0OOO000OO0OO0O0O in O0OO00OOO00O0OO0O ]#line:70
        O0OO00OOO00O0OO0O =[OOOOOOOO00O000O0O for OOOOOOOO00O000O0O in O0OO00OOO00O0OO0O if OOOOOOOO00O000O0O in OO000OO00OOOO0O00 ._columns ]#line:71
        OO0OOO0OOO000OO00 =np .transpose (np .array ([OO000OO00OOOO0O00 ._columns [OO0OOOOOO0O0000O0 ]for OO0OOOOOO0O0000O0 in O0OO00OOO00O0OO0O ]))#line:72
        if OO0OOO0OOO000OO00 .shape [0 ]<=0 or (len (OO0OOO0OOO000OO00 .shape )>1 and OO0OOO0OOO000OO00 .shape [1 ]<=0 ):return False #line:73
        if not isinstance (O00OOO000OOOO0OOO ,(list ,tuple )):#line:75
            O00OOO000OOOO0OOO =(O00OOO000OOOO0OOO ,)#line:76
        O00OOO000OOOO0OOO =[OO000OO00OOOO0O00 ._to_label (OO0OO0O000O0O000O )for OO0OO0O000O0O000O in O00OOO000OOOO0OOO ]#line:77
        O00OOO000OOOO0OOO =[OOO0O000OO0O000O0 for OOO0O000OO0O000O0 in O00OOO000OOOO0OOO if OOO0O000OO0O000O0 in OO000OO00OOOO0O00 ._columns ]#line:78
        O0O000000OOO00O0O =np .transpose (np .array ([OO000OO00OOOO0O00 ._columns [O00OO000O00O0O0OO ]for O00OO000O00O0O0OO in O00OOO000OOOO0OOO ]))#line:79
        if O0O000000OOO00O0O .shape [0 ]<=0 or (len (O0O000000OOO00O0O .shape )>1 and O0O000000OOO00O0O .shape [1 ]<=0 ):return False #line:80
        OO000OO00OOOO0O00 ._regression .fit (OO0OOO0OOO000OO00 ,O0O000000OOO00O0O )#line:82
        O00OO0OOOOO000000 ={}#line:83
        for O0OOOOOO0O0OO0O00 ,OOOOO000O0OOO0000 in enumerate (O00OOO000OOOO0OOO ):#line:84
            O0OO00O000OOOO0O0 =OO000OO00OOOO0O00 ._regression .coef_ [O0OOOOOO0O0OO0O00 ]#line:85
            OO0O000O0O00O00O0 =OO000OO00OOOO0O00 ._regression .intercept_ [O0OOOOOO0O0OO0O00 ]#line:86
            O00000OO0O000OOOO ='{} = '.format (OOOOO000O0OOO0000 )#line:87
            for OO0OO00OO00OO0O00 ,O000OOO0O0O0OO00O in enumerate (O0OO00OOO00O0OO0O ):#line:88
                O00000OO0O000OOOO +='{} * {} + '.format (O0OO00O000OOOO0O0 [OO0OO00OO00OO0O00 ],O000OOO0O0O0OO00O )#line:89
            print (O00000OO0O000OOOO +str (OO0O000O0O00O00O0 ))#line:90
            O00OO0OOOOO000000 [OOOOO000O0OOO0000 ]=tuple (np .append (O0OO00O000OOOO0O0 ,OO0O000O0O00O00O0 ))#line:91
        OO000OO00OOOO0O00 ._result ['xlabels']=O0OO00OOO00O0OO0O #line:92
        OO000OO00OOOO0O00 ._result ['ylabels']=O00OOO000OOOO0OOO #line:93
        OO000OO00OOOO0O00 ._result ['weights']=O00OO0OOOOO000000 #line:94
        return True #line:95
    def get_weight (O00OO0O0O00OOOOO0 ,ylabel ='all'):#line:97
        O0000000OOOO0O00O =O00OO0O0O00OOOOO0 ._result ['weights']#line:98
        if isinstance (ylabel ,str )and ylabel .lower ()=='all':#line:99
            return O0000000OOOO0O00O #line:100
        ylabel =O00OO0O0O00OOOOO0 ._to_label (ylabel )#line:101
        if ylabel in O0000000OOOO0O00O :#line:102
            return O0000000OOOO0O00O [ylabel ]#line:103
        return None #line:104
    def print_labels (O0OOO00OOOOOOO0O0 ):#line:106
        print (O0OOO00OOOOOOO0O0 ._labels )#line:107
    def print_data (O0O0OOO000O0O0000 ):#line:109
        print (O0O0OOO000O0O0000 ._data )#line:110
    def _plot_data_2d (OO0O0OO00000O000O ,OO0000OO00O0OOOO0 ,O000O00OOOOO0O0O0 ,O0O00OOOOO0OOO0O0 ):#line:112
        OO0O00000O000O0OO =len (OO0000OO00O0OOOO0 )#line:113
        OOO000OOOO000OO0O =len (O000O00OOOOO0O0O0 )#line:114
        OOOOO00OOOO0OOO0O =plt .figure ()#line:115
        OOOOOOO0O00OOOO00 =1 #line:116
        for OO00O0OO00OO0OOO0 in OO0000OO00O0OOOO0 :#line:117
            OO00O0OO00OO0OOO0 =OO0O0OO00000O000O ._to_label (OO00O0OO00OO0OOO0 )#line:118
            O0O00O0O000O00O00 =OO0O0OO00000O000O ._get_data (OO00O0OO00OO0OOO0 )#line:119
            if O0O00O0O000O00O00 is not None :#line:120
                for OO0OOOO0OOO0O0OOO ,OO00000OO00000O0O in enumerate (O000O00OOOOO0O0O0 ):#line:121
                    OO00000OO00000O0O =OO0O0OO00000O000O ._to_label (OO00000OO00000O0O )#line:122
                    O00O0OO0O00O00000 =OO0O0OO00000O000O ._get_data (OO00000OO00000O0O )#line:123
                    O0OO0O00O0O000OO0 =OOOOO00OOOO0OOO0O .add_subplot (OO0O00000O000O0OO ,OOO000OOOO000OO0O ,OOOOOOO0O00OOOO00 )#line:124
                    if O00O0OO0O00O00000 is not None :#line:125
                        O0OO0O00O0O000OO0 .scatter (O0O00O0O000O00O00 ,O00O0OO0O00O00000 ,c =O0O00OOOOO0OOO0O0 [OO0OOOO0OOO0O0OOO ])#line:126
                        O0OO0O00O0O000OO0 .set_xlabel (OO00O0OO00OO0OOO0 )#line:127
                        O0OO0O00O0O000OO0 .set_ylabel (OO00000OO00000O0O )#line:128
                        OOOOOOO0O00OOOO00 +=1 #line:129
    def _plot_data_3d (O0OO0OOOO0O00OOOO ,OO000000OOO000000 ,OO0OO00000OO0OO0O ,O0O0O0O000OOO000O ):#line:131
        O000O0O0000O0O0OO =O0OO0OOOO0O00OOOO ._to_label (OO000000OOO000000 [0 ])#line:132
        OOOOOO00OOOOOO00O =O0OO0OOOO0O00OOOO ._to_label (OO000000OOO000000 [1 ])#line:133
        O0OO0OO00OO00O0OO =O0OO0OOOO0O00OOOO ._get_data (O000O0O0000O0O0OO )#line:134
        OOOO0O0OOO000OOOO =O0OO0OOOO0O00OOOO ._get_data (OOOOOO00OOOOOO00O )#line:135
        if O0OO0OO00OO00O0OO is not None and OOOO0O0OOO000OOOO is not None :#line:136
            O0OOOO0OO00000OOO =len (OO0OO00000OO0OO0O )#line:137
            OOOO0O000OO0O0000 =plt .figure ()#line:138
            O0OOO000O0O00O00O =1 #line:139
            for O0O0OO000OOO00OOO ,OOOO0O000OOO0O00O in enumerate (OO0OO00000OO0OO0O ):#line:140
                OOOO0O000OOO0O00O =O0OO0OOOO0O00OOOO ._to_label (OOOO0O000OOO0O00O )#line:141
                O0O0000OO00OOOO00 =O0OO0OOOO0O00OOOO ._get_data (OOOO0O000OOO0O00O )#line:142
                O000O00OOO0O0O0O0 =OOOO0O000OO0O0000 .add_subplot (1 ,O0OOOO0OO00000OOO ,O0OOO000O0O00O00O ,projection ='3d')#line:143
                if O0O0000OO00OOOO00 is not None :#line:144
                    O000O00OOO0O0O0O0 .scatter (O0OO0OO00OO00O0OO ,OOOO0O0OOO000OOOO ,O0O0000OO00OOOO00 ,c =O0O0O0O000OOO000O [O0O0OO000OOO00OOO ])#line:145
                    O000O00OOO0O0O0O0 .set_xlabel (O000O0O0000O0O0OO )#line:146
                    O000O00OOO0O0O0O0 .set_ylabel (OOOOOO00OOOOOO00O )#line:147
                    O000O00OOO0O0O0O0 .set_zlabel (OOOO0O000OOO0O00O )#line:148
                    O0OOO000O0O00O00O +=1 #line:149
    def plot_data (OO00O0O000O0OOOOO ,O00OO0O00O000OOOO ,O00OO00O00OO0000O ,colors ='blue',block =True ):#line:151
        if OO00O0O000O0OOOOO ._data is not None :#line:152
            if not isinstance (O00OO0O00O000OOOO ,(list ,tuple )):#line:153
                O00OO0O00O000OOOO =(O00OO0O00O000OOOO ,)#line:154
            if not isinstance (O00OO00O00OO0000O ,(list ,tuple )):#line:155
                O00OO00O00OO0000O =(O00OO00O00OO0000O ,)#line:156
            if not isinstance (colors ,(list ,tuple )):#line:157
                colors =(colors ,)#line:158
            OOO0O0O000O0O0O00 =len (O00OO00O00OO0000O )-len (colors )#line:159
            if OOO0O0O000O0O0O00 >0 :#line:160
                colors =[O0O0O000OOOO0O0O0 for O0O0O000OOOO0O0O0 in colors ]#line:161
                colors .extend ([colors [-1 ]]*OOO0O0O000O0O0O00 )#line:162
            if len (O00OO0O00O000OOOO )==2 :#line:163
                OO00O0O000O0OOOOO ._plot_data_3d (O00OO0O00O000OOOO ,O00OO00O00OO0000O ,colors )#line:164
            else :#line:165
                OO00O0O000O0OOOOO ._plot_data_2d (O00OO0O00O000OOOO ,O00OO00O00OO0000O ,colors )#line:166
            plt .show (block =block )#line:167
    def _get_prediction_range (O0OOOO0O0OO00O00O ,OOOO0000000O0O000 ):#line:169
        OO0OO0O000OO0OO00 =np .min (OOOO0000000O0O000 )#line:170
        OOOO0000000O0OOOO =np .max (OOOO0000000O0O000 )#line:171
        if OO0OO0O000OO0OO00 ==OOOO0000000O0OOOO :#line:172
            return np .array ([0 ]*11 )#line:173
        else :#line:174
            O0OO000OOOOOOOO0O =(OOOO0000000O0OOOO -OO0OO0O000OO0OO00 )/10 #line:175
            return np .arange (OO0OO0O000OO0OO00 ,OOOO0000000O0OOOO +O0OO000OOOOOOOO0O ,O0OO000OOOOOOOO0O )#line:176
    def _plot_result_2d (OOOOOO0OO0OOO0OOO ,O00O0O0OO0OOOO000 ,OO0O0000OOOOO0O00 ,OOOO00OO0O0O0O0O0 ):#line:178
        O0000O0OO00O000O0 =OOOOOO0OO0OOO0OOO ._to_label (O00O0O0OO0OOOO000 [0 ])#line:179
        OO00OO0OOO0000OOO =OOOOOO0OO0OOO0OOO ._get_data (O0000O0OO00O000O0 )#line:180
        if OO00OO0OOO0000OOO is not None :#line:181
            OOOOO0O0OO000O00O =OOOOOO0OO0OOO0OOO ._get_prediction_range (OO00OO0OOO0000OOO ).reshape (-1 ,1 )#line:182
            OO00O0O0OO00O00O0 =OOOOOO0OO0OOO0OOO ._regression .predict (OOOOO0O0OO000O00O )#line:183
            O0OOO0OOOOO000O0O =len (OO0O0000OOOOO0O00 )#line:185
            OO00OOOO0O000O000 =plt .figure ()#line:186
            O00OO0O0O00O00O0O =1 #line:187
            for O0000000000OO0OO0 ,O00O0O00OO00000OO in enumerate (OO0O0000OOOOO0O00 ):#line:188
                O00O0O00OO00000OO =OOOOOO0OO0OOO0OOO ._to_label (O00O0O00OO00000OO )#line:189
                OOOOO0O0OOOO00OO0 =OOOOOO0OO0OOO0OOO ._get_data (O00O0O00OO00000OO )#line:190
                OOOOO0000OOO00OOO =OOOOOO0OO0OOO0OOO .get_weight (O00O0O00OO00000OO )#line:191
                O0O000000OO00O0OO =OO00OOOO0O000O000 .add_subplot (1 ,O0OOO0OOOOO000O0O ,O00OO0O0O00O00O0O )#line:192
                if OOOOO0O0OOOO00OO0 is not None and OOOOO0000OOO00OOO is not None :#line:193
                    O0O000000OO00O0OO .scatter (OO00OO0OOO0000OOO ,OOOOO0O0OOOO00OO0 ,c =OOOO00OO0O0O0O0O0 [O0000000000OO0OO0 ])#line:194
                    O0O000000OO00O0OO .plot (OOOOO0O0OO000O00O ,OO00O0O0OO00O00O0 [:,O0000000000OO0OO0 ],c ='r')#line:195
                    O0O000000OO00O0OO .set_xlabel (O0000O0OO00O000O0 )#line:196
                    O0O000000OO00O0OO .set_ylabel (O00O0O00OO00000OO )#line:197
                    O00OO0O0O00O00O0O +=1 #line:198
    def _plot_result_3d (O0O00000O00OOO00O ,OO00O0OOOO0OO000O ,O0O00OO000O00OO0O ,OOOO0OO000OOO0000 ):#line:200
        O0O000OOO0O000O0O =O0O00000O00OOO00O ._to_label (OO00O0OOOO0OO000O [0 ])#line:201
        OOOO0OO0O0OO000OO =O0O00000O00OOO00O ._to_label (OO00O0OOOO0OO000O [1 ])#line:202
        O0OO0OO00OOOOO0OO =O0O00000O00OOO00O ._get_data (O0O000OOO0O000O0O )#line:203
        OOOOOOOO0OO0000O0 =O0O00000O00OOO00O ._get_data (OOOO0OO0O0OO000OO )#line:204
        if O0OO0OO00OOOOO0OO is not None and OOOOOOOO0OO0000O0 is not None :#line:205
            OO00O000000000O00 =O0O00000O00OOO00O ._get_prediction_range (O0OO0OO00OOOOO0OO )#line:206
            OOO00000O0O0OO0O0 =O0O00000O00OOO00O ._get_prediction_range (OOOOOOOO0OO0000O0 )#line:207
            O000OOOO0O0O0O0O0 =O0O00000O00OOO00O ._regression .predict (np .array ([(OOO0O000000O0O00O ,O00OO00000OO0000O )for O00OO00000OO0000O in OOO00000O0O0OO0O0 for OOO0O000000O0O00O in OO00O000000000O00 ]))#line:208
            OO00O000000000O00 ,OOO00000O0O0OO0O0 =np .meshgrid (OO00O000000000O00 ,OOO00000O0O0OO0O0 )#line:209
            O00000O0OO0OO0O0O =len (O0O00OO000O00OO0O )#line:211
            OO0O00OO00O000OO0 =plt .figure ()#line:212
            OOOOO0OO00O0OO000 =1 #line:213
            for OO000O0OOOO000OO0 ,O000OOOO000OOO00O in enumerate (O0O00OO000O00OO0O ):#line:214
                O000OOOO000OOO00O =O0O00000O00OOO00O ._to_label (O000OOOO000OOO00O )#line:215
                OOO0OO00O0OO0OO00 =O0O00000O00OOO00O ._get_data (O000OOOO000OOO00O )#line:216
                O00O000O0O0O0OOOO =O0O00000O00OOO00O .get_weight (O000OOOO000OOO00O )#line:217
                OO0000OOOOO000O0O =OO0O00OO00O000OO0 .add_subplot (1 ,O00000O0OO0OO0O0O ,OOOOO0OO00O0OO000 ,projection ='3d')#line:218
                if OOO0OO00O0OO0OO00 is not None and O00O000O0O0O0OOOO is not None :#line:219
                    OO0000OOOOO000O0O .scatter (O0OO0OO00OOOOO0OO ,OOOOOOOO0OO0000O0 ,OOO0OO00O0OO0OO00 ,c =OOOO0OO000OOO0000 [OO000O0OOOO000OO0 ])#line:220
                    OO0000OOOOO000O0O .plot_surface (OO00O000000000O00 ,OOO00000O0O0OO0O0 ,O000OOOO0O0O0O0O0 [:,OO000O0OOOO000OO0 ].reshape (OO00O000000000O00 .shape ),color ='red')#line:221
                    OO0000OOOOO000O0O .set_xlabel (O0O000OOO0O000O0O )#line:222
                    OO0000OOOOO000O0O .set_ylabel (OOOO0OO0O0OO000OO )#line:223
                    OO0000OOOOO000O0O .set_zlabel (O000OOOO000OOO00O )#line:224
                    OOOOO0OO00O0OO000 +=1 #line:225
    def plot_result (OO00OO0000O0O0000 ,colors ='blue',block =True ):#line:227
        if OO00OO0000O0O0000 ._data is not None :#line:228
            OOOOO0OO0OO0O0000 =OO00OO0000O0O0000 ._result ['xlabels']#line:229
            OO0OO0O0OOOOO0OOO =OO00OO0000O0O0000 ._result ['ylabels']#line:230
            if OOOOO0OO0OO0O0000 is not None and OO0OO0O0OOOOO0OOO is not None :#line:231
                if not isinstance (colors ,(list ,tuple )):#line:232
                    colors =(colors ,)#line:233
                OO0OOOOO0OOO0OOO0 =len (OO0OO0O0OOOOO0OOO )-len (colors )#line:234
                if OO0OOOOO0OOO0OOO0 >0 :#line:235
                    colors =[O0O0O0000O0OOO0OO for O0O0O0000O0OOO0OO in colors ]#line:236
                    colors .extend ([colors [-1 ]]*OO0OOOOO0OOO0OOO0 )#line:237
                O0O0O00000000000O =len (OOOOO0OO0OO0O0000 )#line:238
                if O0O0O00000000000O ==1 :#line:239
                    OO00OO0000O0O0000 ._plot_result_2d (OOOOO0OO0OO0O0000 ,OO0OO0O0OOOOO0OOO ,colors )#line:240
                    plt .show (block =block )#line:241
                elif O0O0O00000000000O ==2 :#line:242
                    OO00OO0000O0O0000 ._plot_result_3d (OOOOO0OO0OO0O0000 ,OO0OO0O0OOOOO0OOO ,colors )#line:243
                    plt .show (block =block )#line:244
    def _plot_weight_2d (OOO000OO0O00O0OO0 ,OOOOOOO00OOOO0O00 ,OOO00O0O0O0000000 ,OO0OO00OOOOOOOOOO ,OO00OOO0O000OOO0O ):#line:246
        OOOO0000O0OO0OO00 =OOO000OO0O00O0OO0 ._to_label (OOOOOOO00OOOO0O00 [0 ])#line:247
        OO00O0OO000O00OOO =OOO000OO0O00O0OO0 ._get_data (OOOO0000O0OO0OO00 )#line:248
        if OO00O0OO000O00OOO is not None :#line:249
            O0000O0O0OO0OO000 =OOO000OO0O00O0OO0 ._get_prediction_range (OO00O0OO000O00OOO ).reshape (-1 ,1 )#line:250
            O000O0000O0OOO0O0 =len (OOO00O0O0O0000000 )#line:251
            O00OOOOO000OO0OO0 =plt .figure ()#line:252
            O0OOOO00OO00OO000 =1 #line:253
            for O0OOO000000OO0OO0 ,O0O0O000000000OOO in enumerate (OOO00O0O0O0000000 ):#line:254
                O0O0O000000000OOO =OOO000OO0O00O0OO0 ._to_label (O0O0O000000000OOO )#line:255
                O00O0000000000OO0 =OOO000OO0O00O0OO0 ._get_data (O0O0O000000000OOO )#line:256
                OO000O00O0O0OOO00 =OO0OO00OOOOOOOOOO [O0OOO000000OO0OO0 ]#line:257
                O0OOO00OO0O00OOO0 =OO000O00O0O0OOO00 [0 ]*O0000O0O0OO0OO000 +OO000O00O0O0OOO00 [1 ]#line:258
                OOOO00000O0000000 =O00OOOOO000OO0OO0 .add_subplot (1 ,O000O0000O0OOO0O0 ,O0OOOO00OO00OO000 )#line:259
                if O00O0000000000OO0 is not None :#line:260
                    OOOO00000O0000000 .scatter (OO00O0OO000O00OOO ,O00O0000000000OO0 ,c =OO00OOO0O000OOO0O [O0OOO000000OO0OO0 ])#line:261
                    OOOO00000O0000000 .plot (O0000O0O0OO0OO000 ,O0OOO00OO0O00OOO0 ,c ='r')#line:262
                    OOOO00000O0000000 .set_xlabel (OOOO0000O0OO0OO00 )#line:263
                    OOOO00000O0000000 .set_ylabel (O0O0O000000000OOO )#line:264
                    O0OOOO00OO00OO000 +=1 #line:265
    def _plot_weight_3d (OO00OO0O00OO0OOO0 ,O0OO00OOO000O000O ,OO0OO0O000000O00O ,OOOO0000OOO0OO00O ,O00O0OO0O00OOO0OO ):#line:267
        OOOOOO0O000O00OO0 =OO00OO0O00OO0OOO0 ._to_label (O0OO00OOO000O000O [0 ])#line:268
        OOO0000O000OO000O =OO00OO0O00OO0OOO0 ._to_label (O0OO00OOO000O000O [1 ])#line:269
        OO00O0O00O00000O0 =OO00OO0O00OO0OOO0 ._get_data (OOOOOO0O000O00OO0 )#line:270
        O0O0O0OOO0O0OOO0O =OO00OO0O00OO0OOO0 ._get_data (OOO0000O000OO000O )#line:271
        if OO00O0O00O00000O0 is not None and O0O0O0OOO0O0OOO0O is not None :#line:272
            O0OOO0OOOOO00O000 =OO00OO0O00OO0OOO0 ._get_prediction_range (OO00O0O00O00000O0 )#line:273
            OO00O0O0OO000000O =OO00OO0O00OO0OOO0 ._get_prediction_range (O0O0O0OOO0O0OOO0O )#line:274
            OO00O0O0O00OO0000 ,OOO00OO000O00O000 =np .meshgrid (O0OOO0OOOOO00O000 ,OO00O0O0OO000000O )#line:275
            O0O000OOOOO00OO0O =len (OO0OO0O000000O00O )#line:277
            OOOOOO000OOO00O00 =plt .figure ()#line:278
            OO000OOO0OO00O0O0 =1 #line:279
            for O0O00O0OO0O0OOO00 ,O0O0O000OO0O0OOO0 in enumerate (OO0OO0O000000O00O ):#line:280
                O0O0O000OO0O0OOO0 =OO00OO0O00OO0OOO0 ._to_label (O0O0O000OO0O0OOO0 )#line:281
                OOOO0O0OOOOO00O00 =OO00OO0O00OO0OOO0 ._get_data (O0O0O000OO0O0OOO0 )#line:282
                OOO00O0O0OO00O0O0 =OOOO0000OOO0OO00O [O0O00O0OO0O0OOO00 ]#line:283
                OOO00O00O000000O0 =np .array ([OOO00O0O0OO00O0O0 [0 ]*O00OO00OOO000OOO0 +OOO00O0O0OO00O0O0 [1 ]*OOO0OO000000OO0OO +OOO00O0O0OO00O0O0 [2 ]for OOO0OO000000OO0OO in OO00O0O0OO000000O for O00OO00OOO000OOO0 in O0OOO0OOOOO00O000 ])#line:284
                OO0OO00O0O0O0O000 =OOOOOO000OOO00O00 .add_subplot (1 ,O0O000OOOOO00OO0O ,OO000OOO0OO00O0O0 ,projection ='3d')#line:285
                if OOOO0O0OOOOO00O00 is not None :#line:286
                    OO0OO00O0O0O0O000 .scatter (OO00O0O00O00000O0 ,O0O0O0OOO0O0OOO0O ,OOOO0O0OOOOO00O00 ,c =O00O0OO0O00OOO0OO [O0O00O0OO0O0OOO00 ])#line:287
                    OO0OO00O0O0O0O000 .plot_surface (OO00O0O0O00OO0000 ,OOO00OO000O00O000 ,OOO00O00O000000O0 .reshape (OO00O0O0O00OO0000 .shape ),color ='red')#line:288
                    OO0OO00O0O0O0O000 .set_xlabel (OOOOOO0O000O00OO0 )#line:289
                    OO0OO00O0O0O0O000 .set_ylabel (OOO0000O000OO000O )#line:290
                    OO0OO00O0O0O0O000 .set_zlabel (O0O0O000OO0O0OOO0 )#line:291
                    OO000OOO0OO00O0O0 +=1 #line:292
    def plot_weight (O0O0OOOOO00OO0O00 ,O00O000O0OOOO0OO0 ,OOO0000O0OOO000OO ,OOOOOOOO00O0000O0 ,colors ='blue',block =True ):#line:294
        if O0O0OOOOO00OO0O00 ._data is not None and isinstance (OOOOOOOO00O0000O0 ,(list ,tuple ,dict )):#line:295
            if not isinstance (O00O000O0OOOO0OO0 ,(list ,tuple )):#line:296
                O00O000O0OOOO0OO0 =(O00O000O0OOOO0OO0 ,)#line:297
            if not isinstance (OOO0000O0OOO000OO ,(list ,tuple )):#line:298
                OOO0000O0OOO000OO =(OOO0000O0OOO000OO ,)#line:299
            if isinstance (OOOOOOOO00O0000O0 ,dict ):#line:300
                OOOOOOOO00O0000O0 =[OOOOOOOO00O0000O0 [O00OOOOOO00OO0O0O ]for O00OOOOOO00OO0O0O in OOO0000O0OOO000OO ]#line:301
            elif not isinstance (OOOOOOOO00O0000O0 [0 ],(list ,tuple )):#line:302
                OOOOOOOO00O0000O0 =(OOOOOOOO00O0000O0 ,)#line:303
            if not isinstance (colors ,(list ,tuple )):#line:304
                colors =(colors ,)#line:305
            O0O00000O000OO0OO =len (OOO0000O0OOO000OO )-len (colors )#line:306
            if O0O00000O000OO0OO >0 :#line:307
                colors =[OO0O00O0OO0OOO00O for OO0O00O0OO0OOO00O in colors ]#line:308
                colors .extend ([colors [-1 ]]*O0O00000O000OO0OO )#line:309
            O0000000O000OO0O0 =len (O00O000O0OOOO0OO0 )#line:310
            if O0000000O000OO0O0 ==1 :#line:311
                O0O0OOOOO00OO0O00 ._plot_weight_2d (O00O000O0OOOO0OO0 ,OOO0000O0OOO000OO ,OOOOOOOO00O0000O0 ,colors )#line:312
                plt .show (block =block )#line:313
            elif O0000000O000OO0O0 ==2 :#line:314
                O0O0OOOOO00OO0O00 ._plot_weight_3d (O00O000O0OOOO0OO0 ,OOO0000O0OOO000OO ,OOOOOOOO00O0000O0 ,colors )#line:315
                plt .show (block =block )#line:316
