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
    def __init__ (OO000O0O000O00O00 ):#line:8
        OO000O0O000O00O00 ._regression =Regression ()#line:9
        OO000O0O000O00O00 ._clear ()#line:10
    def _clear (O0O0OO00O0OOOO0O0 ):#line:12
        O0O0OO00O0OOOO0O0 ._labels =None #line:13
        O0O0OO00O0OOOO0O0 ._data =None #line:14
        O0O0OO00O0OOOO0O0 ._columns ={}#line:15
        O0O0OO00O0OOOO0O0 ._clear_result ()#line:16
    def _clear_result (OO00000O00000000O ):#line:18
        OO00000O00000000O ._result ={'xlabels':None ,'ylabels':None ,'weights':{}}#line:23
    def _to_label (OO0O0OO0O000OOOOO ,OOO0OO00OOO0O000O ):#line:25
        if OO0O0OO0O000OOOOO ._labels is not None :#line:26
            if isinstance (OOO0OO00OOO0O000O ,(int ,float )):#line:27
                OOO0OO00OOO0O000O =int (OOO0OO00OOO0O000O )#line:28
                if OOO0OO00OOO0O000O >=0 and OOO0OO00OOO0O000O <len (OO0O0OO0O000OOOOO ._labels ):#line:29
                    return OO0O0OO0O000OOOOO ._labels [OOO0OO00OOO0O000O ]#line:30
            elif isinstance (OOO0OO00OOO0O000O ,str ):#line:31
                if OOO0OO00OOO0O000O in OO0O0OO0O000OOOOO ._labels :#line:32
                    return OOO0OO00OOO0O000O #line:33
        return None #line:34
    def load_data (O0OOOOOO00OOOOO00 ,O0O00OO00O00O0OO0 ):#line:36
        O0OOOOOO00OOOOO00 ._clear ()#line:37
        O0OOOOOO00OOOOO00 ._labels =np .loadtxt (O0O00OO00O00O0OO0 ,dtype ='str',delimiter =',',max_rows =1 )#line:38
        O0OOOOOO00OOOOO00 ._data =np .loadtxt (O0O00OO00O00O0OO0 ,delimiter =',',skiprows =1 )#line:39
        for O000O0OO0OO000O00 ,O0O000O00O0OO00OO in enumerate (O0OOOOOO00OOOOO00 ._labels ):#line:40
            O0OOOOOO00OOOOO00 ._columns [O0O000O00O0OO00OO ]=O0OOOOOO00OOOOO00 ._data [:,O000O0OO0OO000O00 ]#line:41
        return O0OOOOOO00OOOOO00 ._data #line:42
    def get_label (O0O0OO0OO00000O00 ,index ='all'):#line:44
        if O0O0OO0OO00000O00 ._labels is not None :#line:45
            if isinstance (index ,(int ,float )):#line:46
                index =int (index )#line:47
                if index >=0 and index <len (O0O0OO0OO00000O00 ._labels ):#line:48
                    return O0O0OO0OO00000O00 ._labels [index ]#line:49
            elif isinstance (index ,str ):#line:50
                if index .lower ()=='all':#line:51
                    return O0O0OO0OO00000O00 ._labels #line:52
        return None #line:53
    def _get_data (O0O0OO0000O000O0O ,O0OOO0OOOOOOO00OO ):#line:55
        if O0OOO0OOOOOOO00OO is not None and O0OOO0OOOOOOO00OO in O0O0OO0000O000O0O ._columns :#line:56
            return O0O0OO0000O000O0O ._columns [O0OOO0OOOOOOO00OO ]#line:57
        return None #line:58
    def get_data (OOOO0000OO0O0OOOO ,label ='all'):#line:60
        if isinstance (label ,str )and label .lower ()=='all':#line:61
            return OOOO0000OO0O0OOOO ._data #line:62
        label =OOOO0000OO0O0OOOO ._to_label (label )#line:63
        return OOOO0000OO0O0OOOO ._get_data (label )#line:64
    def fit (O0000OO00O0OO0O0O ,O00OOOOO000OO0000 ,OOO0OOO00O0OOO0OO ):#line:66
        O0000OO00O0OO0O0O ._clear_result ()#line:67
        if not isinstance (O00OOOOO000OO0000 ,(list ,tuple )):#line:68
            O00OOOOO000OO0000 =(O00OOOOO000OO0000 ,)#line:69
        O00OOOOO000OO0000 =[O0000OO00O0OO0O0O ._to_label (O00O00OOO0000O0OO )for O00O00OOO0000O0OO in O00OOOOO000OO0000 ]#line:70
        O00OOOOO000OO0000 =[O0OO00OOO0O0O0000 for O0OO00OOO0O0O0000 in O00OOOOO000OO0000 if O0OO00OOO0O0O0000 in O0000OO00O0OO0O0O ._columns ]#line:71
        OOOO00O00OO0OO0O0 =np .transpose (np .array ([O0000OO00O0OO0O0O ._columns [OO0OOOOO0O00OOO00 ]for OO0OOOOO0O00OOO00 in O00OOOOO000OO0000 ]))#line:72
        if OOOO00O00OO0OO0O0 .shape [0 ]<=0 or (len (OOOO00O00OO0OO0O0 .shape )>1 and OOOO00O00OO0OO0O0 .shape [1 ]<=0 ):return False #line:73
        if not isinstance (OOO0OOO00O0OOO0OO ,(list ,tuple )):#line:75
            OOO0OOO00O0OOO0OO =(OOO0OOO00O0OOO0OO ,)#line:76
        OOO0OOO00O0OOO0OO =[O0000OO00O0OO0O0O ._to_label (OOO0O00O0O00OO000 )for OOO0O00O0O00OO000 in OOO0OOO00O0OOO0OO ]#line:77
        OOO0OOO00O0OOO0OO =[OOO0000O0OOOOOO0O for OOO0000O0OOOOOO0O in OOO0OOO00O0OOO0OO if OOO0000O0OOOOOO0O in O0000OO00O0OO0O0O ._columns ]#line:78
        OOO000OO000O0O0O0 =np .transpose (np .array ([O0000OO00O0OO0O0O ._columns [OO0O0O00OO00O0O00 ]for OO0O0O00OO00O0O00 in OOO0OOO00O0OOO0OO ]))#line:79
        if OOO000OO000O0O0O0 .shape [0 ]<=0 or (len (OOO000OO000O0O0O0 .shape )>1 and OOO000OO000O0O0O0 .shape [1 ]<=0 ):return False #line:80
        O0000OO00O0OO0O0O ._regression .fit (OOOO00O00OO0OO0O0 ,OOO000OO000O0O0O0 )#line:82
        O0O000O0OO00OO000 ={}#line:83
        for O0OOOO0OO00O00O00 ,O0O000OOOOO0OO000 in enumerate (OOO0OOO00O0OOO0OO ):#line:84
            OOO000000OO00O0O0 =O0000OO00O0OO0O0O ._regression .coef_ [O0OOOO0OO00O00O00 ]#line:85
            OOO00O00000O0OOO0 =O0000OO00O0OO0O0O ._regression .intercept_ [O0OOOO0OO00O00O00 ]#line:86
            OOO000O000OO0OO0O ='{} = '.format (O0O000OOOOO0OO000 )#line:87
            for O00OOOO0OO00O0OO0 ,O0OO00OOOOO00O000 in enumerate (O00OOOOO000OO0000 ):#line:88
                OOO000O000OO0OO0O +='{} * {} + '.format (OOO000000OO00O0O0 [O00OOOO0OO00O0OO0 ],O0OO00OOOOO00O000 )#line:89
            print (OOO000O000OO0OO0O +str (OOO00O00000O0OOO0 ))#line:90
            O0O000O0OO00OO000 [O0O000OOOOO0OO000 ]=tuple (np .append (OOO000000OO00O0O0 ,OOO00O00000O0OOO0 ))#line:91
        O0000OO00O0OO0O0O ._result ['xlabels']=O00OOOOO000OO0000 #line:92
        O0000OO00O0OO0O0O ._result ['ylabels']=OOO0OOO00O0OOO0OO #line:93
        O0000OO00O0OO0O0O ._result ['weights']=O0O000O0OO00OO000 #line:94
        return True #line:95
    def get_weight (OO000OO0OOOO0OO00 ,ylabel ='all'):#line:97
        O0OO0OO0OO0O0000O =OO000OO0OOOO0OO00 ._result ['weights']#line:98
        if isinstance (ylabel ,str )and ylabel .lower ()=='all':#line:99
            return O0OO0OO0OO0O0000O #line:100
        ylabel =OO000OO0OOOO0OO00 ._to_label (ylabel )#line:101
        if ylabel in O0OO0OO0OO0O0000O :#line:102
            return O0OO0OO0OO0O0000O [ylabel ]#line:103
        return None #line:104
    def print_labels (O00OO000O000000O0 ):#line:106
        print (O00OO000O000000O0 ._labels )#line:107
    def print_data (O0O0O000O0000OO00 ):#line:109
        print (O0O0O000O0000OO00 ._data )#line:110
    def _plot_data_2d (O000O0OOO00O0OO0O ,O00OOOOO0OO0OOO0O ,OOO000O000O0O0OOO ,O000O000000O0OO0O ):#line:112
        OO00OOOO0OOOOOO0O =len (O00OOOOO0OO0OOO0O )#line:113
        O0OOOO0OOOOOO0OOO =len (OOO000O000O0O0OOO )#line:114
        O00O0O0O0O00O0OOO =plt .figure ()#line:115
        OOO0O00O0OOO0O0O0 =1 #line:116
        for O00OO0O000000O0OO in O00OOOOO0OO0OOO0O :#line:117
            O00OO0O000000O0OO =O000O0OOO00O0OO0O ._to_label (O00OO0O000000O0OO )#line:118
            O0O00O00000OO0OOO =O000O0OOO00O0OO0O ._get_data (O00OO0O000000O0OO )#line:119
            if O0O00O00000OO0OOO is not None :#line:120
                for O000O0O0OO00000O0 ,OO000O00OOOOO0OOO in enumerate (OOO000O000O0O0OOO ):#line:121
                    OO000O00OOOOO0OOO =O000O0OOO00O0OO0O ._to_label (OO000O00OOOOO0OOO )#line:122
                    O0OO00OO0OO0O0000 =O000O0OOO00O0OO0O ._get_data (OO000O00OOOOO0OOO )#line:123
                    O000OO0000OO00OOO =O00O0O0O0O00O0OOO .add_subplot (OO00OOOO0OOOOOO0O ,O0OOOO0OOOOOO0OOO ,OOO0O00O0OOO0O0O0 )#line:124
                    if O0OO00OO0OO0O0000 is not None :#line:125
                        O000OO0000OO00OOO .scatter (O0O00O00000OO0OOO ,O0OO00OO0OO0O0000 ,c =O000O000000O0OO0O [O000O0O0OO00000O0 ])#line:126
                        O000OO0000OO00OOO .set_xlabel (O00OO0O000000O0OO )#line:127
                        O000OO0000OO00OOO .set_ylabel (OO000O00OOOOO0OOO )#line:128
                        OOO0O00O0OOO0O0O0 +=1 #line:129
    def _plot_data_3d (O000000OO000000OO ,O000000O0O0000O0O ,OO0O0OO00O00OO0OO ,O0OOOO0O0O00OO0O0 ):#line:131
        O0OO0OO0000O00000 =O000000OO000000OO ._to_label (O000000O0O0000O0O [0 ])#line:132
        OOOO0OO0OO0000OO0 =O000000OO000000OO ._to_label (O000000O0O0000O0O [1 ])#line:133
        OO0O0O000OOOOO0O0 =O000000OO000000OO ._get_data (O0OO0OO0000O00000 )#line:134
        OOO00OO00OO0OOOO0 =O000000OO000000OO ._get_data (OOOO0OO0OO0000OO0 )#line:135
        if OO0O0O000OOOOO0O0 is not None and OOO00OO00OO0OOOO0 is not None :#line:136
            O0OOO000OO000O00O =len (OO0O0OO00O00OO0OO )#line:137
            OO0O000O0O0O0OOO0 =plt .figure ()#line:138
            OOOO0000O0O0000O0 =1 #line:139
            for O0O00O0O0O0000O0O ,O0OOO00O0O00OO0OO in enumerate (OO0O0OO00O00OO0OO ):#line:140
                O0OOO00O0O00OO0OO =O000000OO000000OO ._to_label (O0OOO00O0O00OO0OO )#line:141
                O0O0000OOOO000OOO =O000000OO000000OO ._get_data (O0OOO00O0O00OO0OO )#line:142
                OOO0OOOO0OO0O0OOO =OO0O000O0O0O0OOO0 .add_subplot (1 ,O0OOO000OO000O00O ,OOOO0000O0O0000O0 ,projection ='3d')#line:143
                if O0O0000OOOO000OOO is not None :#line:144
                    OOO0OOOO0OO0O0OOO .scatter (OO0O0O000OOOOO0O0 ,OOO00OO00OO0OOOO0 ,O0O0000OOOO000OOO ,c =O0OOOO0O0O00OO0O0 [O0O00O0O0O0000O0O ])#line:145
                    OOO0OOOO0OO0O0OOO .set_xlabel (O0OO0OO0000O00000 )#line:146
                    OOO0OOOO0OO0O0OOO .set_ylabel (OOOO0OO0OO0000OO0 )#line:147
                    OOO0OOOO0OO0O0OOO .set_zlabel (O0OOO00O0O00OO0OO )#line:148
                    OOOO0000O0O0000O0 +=1 #line:149
    def plot_data (OO0OO00OO00OO0000 ,O0O0O0O00O0O00O00 ,OO00OOO00OOOO0O00 ,colors ='blue',block =True ):#line:151
        if OO0OO00OO00OO0000 ._data is not None :#line:152
            if not isinstance (O0O0O0O00O0O00O00 ,(list ,tuple )):#line:153
                O0O0O0O00O0O00O00 =(O0O0O0O00O0O00O00 ,)#line:154
            if not isinstance (OO00OOO00OOOO0O00 ,(list ,tuple )):#line:155
                OO00OOO00OOOO0O00 =(OO00OOO00OOOO0O00 ,)#line:156
            if not isinstance (colors ,(list ,tuple )):#line:157
                colors =(colors ,)#line:158
            OO00O00OOOOO00OO0 =len (OO00OOO00OOOO0O00 )-len (colors )#line:159
            if OO00O00OOOOO00OO0 >0 :#line:160
                colors =[OOOOOO00OO000OO0O for OOOOOO00OO000OO0O in colors ]#line:161
                colors .extend ([colors [-1 ]]*OO00O00OOOOO00OO0 )#line:162
            if len (O0O0O0O00O0O00O00 )==2 :#line:163
                OO0OO00OO00OO0000 ._plot_data_3d (O0O0O0O00O0O00O00 ,OO00OOO00OOOO0O00 ,colors )#line:164
            else :#line:165
                OO0OO00OO00OO0000 ._plot_data_2d (O0O0O0O00O0O00O00 ,OO00OOO00OOOO0O00 ,colors )#line:166
            plt .show (block =block )#line:167
    def _get_prediction_range (OO00OO0OO0OOO0000 ,OO000OO00000O0000 ):#line:169
        OOOO00OOOO0O0OOOO =np .min (OO000OO00000O0000 )#line:170
        O00OO00OO0OOOOO00 =np .max (OO000OO00000O0000 )#line:171
        if OOOO00OOOO0O0OOOO ==O00OO00OO0OOOOO00 :#line:172
            return np .array ([0 ]*11 )#line:173
        else :#line:174
            OO0OO00OO00O000O0 =(O00OO00OO0OOOOO00 -OOOO00OOOO0O0OOOO )/10 #line:175
            return np .arange (OOOO00OOOO0O0OOOO ,O00OO00OO0OOOOO00 +OO0OO00OO00O000O0 ,OO0OO00OO00O000O0 )#line:176
    def _plot_result_2d (O000OO0000OO000O0 ,O0OO000OOO000O000 ,O00O000OOO00OO0OO ,O0OOO0000O0OOO000 ):#line:178
        OOOO0OO00O00OO0OO =O000OO0000OO000O0 ._to_label (O0OO000OOO000O000 [0 ])#line:179
        OO00OO000O00O0OOO =O000OO0000OO000O0 ._get_data (OOOO0OO00O00OO0OO )#line:180
        if OO00OO000O00O0OOO is not None :#line:181
            O00000OO00000O000 =O000OO0000OO000O0 ._get_prediction_range (OO00OO000O00O0OOO ).reshape (-1 ,1 )#line:182
            OOOOO0OO00OOOO0O0 =O000OO0000OO000O0 ._regression .predict (O00000OO00000O000 )#line:183
            OO0OOO0OOOOOO0OOO =len (O00O000OOO00OO0OO )#line:185
            OOOO00O0000000O00 =plt .figure ()#line:186
            OO0O000O0OO00OO00 =1 #line:187
            for OOOOOO00O0OOOO00O ,O00O0OO000O0000O0 in enumerate (O00O000OOO00OO0OO ):#line:188
                O00O0OO000O0000O0 =O000OO0000OO000O0 ._to_label (O00O0OO000O0000O0 )#line:189
                O00O0OO000000000O =O000OO0000OO000O0 ._get_data (O00O0OO000O0000O0 )#line:190
                OOO00OOOO00000OOO =O000OO0000OO000O0 .get_weight (O00O0OO000O0000O0 )#line:191
                OOOO0O0OO000OO0O0 =OOOO00O0000000O00 .add_subplot (1 ,OO0OOO0OOOOOO0OOO ,OO0O000O0OO00OO00 )#line:192
                if O00O0OO000000000O is not None and OOO00OOOO00000OOO is not None :#line:193
                    OOOO0O0OO000OO0O0 .scatter (OO00OO000O00O0OOO ,O00O0OO000000000O ,c =O0OOO0000O0OOO000 [OOOOOO00O0OOOO00O ])#line:194
                    OOOO0O0OO000OO0O0 .plot (O00000OO00000O000 ,OOOOO0OO00OOOO0O0 [:,OOOOOO00O0OOOO00O ],c ='r')#line:195
                    OOOO0O0OO000OO0O0 .set_xlabel (OOOO0OO00O00OO0OO )#line:196
                    OOOO0O0OO000OO0O0 .set_ylabel (O00O0OO000O0000O0 )#line:197
                    OO0O000O0OO00OO00 +=1 #line:198
    def _plot_result_3d (O000OOO00O00OO0O0 ,OOO00O00O00OO00O0 ,OO00OO00O0O0OOOO0 ,OOO00O0OOOOOO00O0 ):#line:200
        O00O0000OO00O00OO =O000OOO00O00OO0O0 ._to_label (OOO00O00O00OO00O0 [0 ])#line:201
        OO00O0000O0O00O0O =O000OOO00O00OO0O0 ._to_label (OOO00O00O00OO00O0 [1 ])#line:202
        O00O0O0OOOOO0OO0O =O000OOO00O00OO0O0 ._get_data (O00O0000OO00O00OO )#line:203
        O0OOO0OOOO0OO000O =O000OOO00O00OO0O0 ._get_data (OO00O0000O0O00O0O )#line:204
        if O00O0O0OOOOO0OO0O is not None and O0OOO0OOOO0OO000O is not None :#line:205
            OO0O0O00000000000 =O000OOO00O00OO0O0 ._get_prediction_range (O00O0O0OOOOO0OO0O )#line:206
            O000O0000O0O000O0 =O000OOO00O00OO0O0 ._get_prediction_range (O0OOO0OOOO0OO000O )#line:207
            OOO000O0O0O0OOO0O =O000OOO00O00OO0O0 ._regression .predict (np .array ([(OOOOO00O0OOOO0O0O ,O0O00O0000O00OOOO )for O0O00O0000O00OOOO in O000O0000O0O000O0 for OOOOO00O0OOOO0O0O in OO0O0O00000000000 ]))#line:208
            OO0O0O00000000000 ,O000O0000O0O000O0 =np .meshgrid (OO0O0O00000000000 ,O000O0000O0O000O0 )#line:209
            O00OOO0O000000O00 =len (OO00OO00O0O0OOOO0 )#line:211
            O00OOOO000O0OO0OO =plt .figure ()#line:212
            OO00O0O0O0O0O000O =1 #line:213
            for OO00OOOO0OOO00O00 ,O000O00O00O00O00O in enumerate (OO00OO00O0O0OOOO0 ):#line:214
                O000O00O00O00O00O =O000OOO00O00OO0O0 ._to_label (O000O00O00O00O00O )#line:215
                OOO0000OOO0O00O0O =O000OOO00O00OO0O0 ._get_data (O000O00O00O00O00O )#line:216
                O00O0OO000OOOO0OO =O000OOO00O00OO0O0 .get_weight (O000O00O00O00O00O )#line:217
                O0OO0OOO0000OO0O0 =O00OOOO000O0OO0OO .add_subplot (1 ,O00OOO0O000000O00 ,OO00O0O0O0O0O000O ,projection ='3d')#line:218
                if OOO0000OOO0O00O0O is not None and O00O0OO000OOOO0OO is not None :#line:219
                    O0OO0OOO0000OO0O0 .scatter (O00O0O0OOOOO0OO0O ,O0OOO0OOOO0OO000O ,OOO0000OOO0O00O0O ,c =OOO00O0OOOOOO00O0 [OO00OOOO0OOO00O00 ])#line:220
                    O0OO0OOO0000OO0O0 .plot_surface (OO0O0O00000000000 ,O000O0000O0O000O0 ,OOO000O0O0O0OOO0O [:,OO00OOOO0OOO00O00 ].reshape (OO0O0O00000000000 .shape ),color ='red')#line:221
                    O0OO0OOO0000OO0O0 .set_xlabel (O00O0000OO00O00OO )#line:222
                    O0OO0OOO0000OO0O0 .set_ylabel (OO00O0000O0O00O0O )#line:223
                    O0OO0OOO0000OO0O0 .set_zlabel (O000O00O00O00O00O )#line:224
                    OO00O0O0O0O0O000O +=1 #line:225
    def plot_result (OO0O00OOO000000OO ,colors ='blue',block =True ):#line:227
        if OO0O00OOO000000OO ._data is not None :#line:228
            OO0OO000O00O00O0O =OO0O00OOO000000OO ._result ['xlabels']#line:229
            OO0OO000O0OOO0000 =OO0O00OOO000000OO ._result ['ylabels']#line:230
            if OO0OO000O00O00O0O is not None and OO0OO000O0OOO0000 is not None :#line:231
                if not isinstance (colors ,(list ,tuple )):#line:232
                    colors =(colors ,)#line:233
                OOO00OOOO0OOOOOO0 =len (OO0OO000O0OOO0000 )-len (colors )#line:234
                if OOO00OOOO0OOOOOO0 >0 :#line:235
                    colors =[O0O0OO0OO00O0O000 for O0O0OO0OO00O0O000 in colors ]#line:236
                    colors .extend ([colors [-1 ]]*OOO00OOOO0OOOOOO0 )#line:237
                OO0O0OO000O0000OO =len (OO0OO000O00O00O0O )#line:238
                if OO0O0OO000O0000OO ==1 :#line:239
                    OO0O00OOO000000OO ._plot_result_2d (OO0OO000O00O00O0O ,OO0OO000O0OOO0000 ,colors )#line:240
                    plt .show (block =block )#line:241
                elif OO0O0OO000O0000OO ==2 :#line:242
                    OO0O00OOO000000OO ._plot_result_3d (OO0OO000O00O00O0O ,OO0OO000O0OOO0000 ,colors )#line:243
                    plt .show (block =block )#line:244
    def _plot_weight_2d (O00OOOO0OO0OOO000 ,OO000O0O00OO0O0OO ,OO0000O00O000000O ,OOO000O0OOOOO0000 ,OO0O0OO00O0OO00OO ):#line:246
        OOO0O0O000OOOO00O =O00OOOO0OO0OOO000 ._to_label (OO000O0O00OO0O0OO [0 ])#line:247
        O0OO0OO00OO0O0O0O =O00OOOO0OO0OOO000 ._get_data (OOO0O0O000OOOO00O )#line:248
        if O0OO0OO00OO0O0O0O is not None :#line:249
            OOO0OO0O000O0OO0O =O00OOOO0OO0OOO000 ._get_prediction_range (O0OO0OO00OO0O0O0O ).reshape (-1 ,1 )#line:250
            OOOO00000O00O000O =len (OO0000O00O000000O )#line:251
            O0O0O0OOOOO000000 =plt .figure ()#line:252
            O0000OO0OOO0OO0O0 =1 #line:253
            for OOOOO0O000OOOO000 ,OO0O0O0O00000O0OO in enumerate (OO0000O00O000000O ):#line:254
                OO0O0O0O00000O0OO =O00OOOO0OO0OOO000 ._to_label (OO0O0O0O00000O0OO )#line:255
                OO0OO0OOOO0O00OO0 =O00OOOO0OO0OOO000 ._get_data (OO0O0O0O00000O0OO )#line:256
                OOOO0O000O0000OOO =OOO000O0OOOOO0000 [OOOOO0O000OOOO000 ]#line:257
                O0O0O00O00O0O0OOO =OOOO0O000O0000OOO [0 ]*OOO0OO0O000O0OO0O +OOOO0O000O0000OOO [1 ]#line:258
                O0O0O0O0OO0000O0O =O0O0O0OOOOO000000 .add_subplot (1 ,OOOO00000O00O000O ,O0000OO0OOO0OO0O0 )#line:259
                if OO0OO0OOOO0O00OO0 is not None :#line:260
                    O0O0O0O0OO0000O0O .scatter (O0OO0OO00OO0O0O0O ,OO0OO0OOOO0O00OO0 ,c =OO0O0OO00O0OO00OO [OOOOO0O000OOOO000 ])#line:261
                    O0O0O0O0OO0000O0O .plot (OOO0OO0O000O0OO0O ,O0O0O00O00O0O0OOO ,c ='r')#line:262
                    O0O0O0O0OO0000O0O .set_xlabel (OOO0O0O000OOOO00O )#line:263
                    O0O0O0O0OO0000O0O .set_ylabel (OO0O0O0O00000O0OO )#line:264
                    O0000OO0OOO0OO0O0 +=1 #line:265
    def _plot_weight_3d (O0000OO0OOOO0OOOO ,O0OO0O0OO00O0O0O0 ,O0O0O00OOO00O00O0 ,O0OOO0O000000O00O ,OOO0O000O0O00O0OO ):#line:267
        O00OO0O0000O00OO0 =O0000OO0OOOO0OOOO ._to_label (O0OO0O0OO00O0O0O0 [0 ])#line:268
        O000OOO000OO00OO0 =O0000OO0OOOO0OOOO ._to_label (O0OO0O0OO00O0O0O0 [1 ])#line:269
        OO0O00000O00000OO =O0000OO0OOOO0OOOO ._get_data (O00OO0O0000O00OO0 )#line:270
        O0OO0O0O0O0OO0000 =O0000OO0OOOO0OOOO ._get_data (O000OOO000OO00OO0 )#line:271
        if OO0O00000O00000OO is not None and O0OO0O0O0O0OO0000 is not None :#line:272
            O0OO0O0O00OO0OOOO =O0000OO0OOOO0OOOO ._get_prediction_range (OO0O00000O00000OO )#line:273
            OOO0O0O000O000OO0 =O0000OO0OOOO0OOOO ._get_prediction_range (O0OO0O0O0O0OO0000 )#line:274
            OOOO0OOOOOOO0OOO0 ,OOOO0O00O0O0OO0O0 =np .meshgrid (O0OO0O0O00OO0OOOO ,OOO0O0O000O000OO0 )#line:275
            O0000OOO0O00OOO0O =len (O0O0O00OOO00O00O0 )#line:277
            O0O0O00O000000OOO =plt .figure ()#line:278
            OOOO000O000OOO0OO =1 #line:279
            for O0OOOOO0O00000OOO ,OO0000OOOOO0O00O0 in enumerate (O0O0O00OOO00O00O0 ):#line:280
                OO0000OOOOO0O00O0 =O0000OO0OOOO0OOOO ._to_label (OO0000OOOOO0O00O0 )#line:281
                O00OOO0O000OOO000 =O0000OO0OOOO0OOOO ._get_data (OO0000OOOOO0O00O0 )#line:282
                OOO0O0O00OOO0000O =O0OOO0O000000O00O [O0OOOOO0O00000OOO ]#line:283
                O0O0OOO00O00O0000 =np .array ([OOO0O0O00OOO0000O [0 ]*O0O0O00OO0000O0O0 +OOO0O0O00OOO0000O [1 ]*OO00OOO0O0O00O0OO +OOO0O0O00OOO0000O [2 ]for OO00OOO0O0O00O0OO in OOO0O0O000O000OO0 for O0O0O00OO0000O0O0 in O0OO0O0O00OO0OOOO ])#line:284
                OO00OO0OO0OOO00O0 =O0O0O00O000000OOO .add_subplot (1 ,O0000OOO0O00OOO0O ,OOOO000O000OOO0OO ,projection ='3d')#line:285
                if O00OOO0O000OOO000 is not None :#line:286
                    OO00OO0OO0OOO00O0 .scatter (OO0O00000O00000OO ,O0OO0O0O0O0OO0000 ,O00OOO0O000OOO000 ,c =OOO0O000O0O00O0OO [O0OOOOO0O00000OOO ])#line:287
                    OO00OO0OO0OOO00O0 .plot_surface (OOOO0OOOOOOO0OOO0 ,OOOO0O00O0O0OO0O0 ,O0O0OOO00O00O0000 .reshape (OOOO0OOOOOOO0OOO0 .shape ),color ='red')#line:288
                    OO00OO0OO0OOO00O0 .set_xlabel (O00OO0O0000O00OO0 )#line:289
                    OO00OO0OO0OOO00O0 .set_ylabel (O000OOO000OO00OO0 )#line:290
                    OO00OO0OO0OOO00O0 .set_zlabel (OO0000OOOOO0O00O0 )#line:291
                    OOOO000O000OOO0OO +=1 #line:292
    def plot_weight (OOOO00000000000OO ,O00O0OO00O00OOOOO ,OO000OO0000O00O0O ,OOOO0OO00000OO0O0 ,colors ='blue',block =True ):#line:294
        if OOOO00000000000OO ._data is not None and isinstance (OOOO0OO00000OO0O0 ,(list ,tuple ,dict )):#line:295
            if not isinstance (O00O0OO00O00OOOOO ,(list ,tuple )):#line:296
                O00O0OO00O00OOOOO =(O00O0OO00O00OOOOO ,)#line:297
            if not isinstance (OO000OO0000O00O0O ,(list ,tuple )):#line:298
                OO000OO0000O00O0O =(OO000OO0000O00O0O ,)#line:299
            if isinstance (OOOO0OO00000OO0O0 ,dict ):#line:300
                OOOO0OO00000OO0O0 =[OOOO0OO00000OO0O0 [O00OO0O0O0OOOO000 ]for O00OO0O0O0OOOO000 in OO000OO0000O00O0O ]#line:301
            elif not isinstance (OOOO0OO00000OO0O0 [0 ],(list ,tuple )):#line:302
                OOOO0OO00000OO0O0 =(OOOO0OO00000OO0O0 ,)#line:303
            if not isinstance (colors ,(list ,tuple )):#line:304
                colors =(colors ,)#line:305
            O0OO0O00O000O0000 =len (OO000OO0000O00O0O )-len (colors )#line:306
            if O0OO0O00O000O0000 >0 :#line:307
                colors =[OOOOO0OOOOOO0OOO0 for OOOOO0OOOOOO0OOO0 in colors ]#line:308
                colors .extend ([colors [-1 ]]*O0OO0O00O000O0000 )#line:309
            OOOOO0OO0O0OO0O0O =len (O00O0OO00O00OOOOO )#line:310
            if OOOOO0OO0O0OO0O0O ==1 :#line:311
                OOOO00000000000OO ._plot_weight_2d (O00O0OO00O00OOOOO ,OO000OO0000O00O0O ,OOOO0OO00000OO0O0 ,colors )#line:312
                plt .show (block =block )#line:313
            elif OOOOO0OO0O0OO0O0O ==2 :#line:314
                OOOO00000000000OO ._plot_weight_3d (O00O0OO00O00OOOOO ,OO000OO0000O00O0O ,OOOO0OO00000OO0O0 ,colors )#line:315
                plt .show (block =block )#line:316
