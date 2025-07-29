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
import cv2 #line:3
np .set_printoptions (suppress =True )#line:5
class TmImage :#line:8
    def __init__ (OO0OOOOO000O0OOO0 ,square ='center'):#line:9
        OO0OOOOO000O0OOO0 ._loaded =False #line:10
        OO0OOOOO000O0OOO0 ._model =None #line:11
        OO0OOOOO000O0OOO0 ._data =np .ndarray (shape =(1 ,224 ,224 ,3 ),dtype =np .float32 )#line:12
        OO0OOOOO000O0OOO0 .set_square (square )#line:13
        OO0OOOOO000O0OOO0 ._clear ()#line:14
    def _clear (OOO0O0OO0OOOO0OO0 ):#line:16
        OOO0O0OO0OOOO0OO0 ._best_label =''#line:17
        OOO0O0OO0OOOO0OO0 ._best_confidence =0 #line:18
        OOO0O0OO0OOOO0OO0 ._labels =[]#line:19
        OOO0O0OO0OOOO0OO0 ._confidences =[]#line:20
    def load_model (O000O00O00OOO0O0O ,OOOO0OOO0OO0O00O0 ):#line:22
        import os #line:23
        os .environ ["TF_USE_LEGACY_KERAS"]="1"#line:24
        import tensorflow as tf #line:25
        O000O00O00OOO0O0O ._loaded =False #line:26
        try :#line:27
            OO0O0O00OO0000OO0 =os .path .join (OOOO0OOO0OO0O00O0 ,'keras_model.h5')#line:28
            OOO000O0OOO0O0O0O =os .path .join (OOOO0OOO0OO0O00O0 ,'labels.txt')#line:29
            O000O00O00OOO0O0O ._model =tf .keras .models .load_model (OO0O0O00OO0000OO0 ,compile =False )#line:30
            with open (OOO000O0OOO0O0O0O ,'r',encoding ='utf8')as O0O0OO00O00O0O000 :#line:31
                O0O0O0O000000O0OO =O0O0OO00O00O0O000 .readlines ()#line:32
                O000O00O00OOO0O0O ._labels =np .array ([OOO00O0O0O0OOO0OO [OOO00O0O0O0OOO0OO .find (' ')+1 :].strip ()for OOO00O0O0O0OOO0OO in O0O0O0O000000O0OO ])#line:33
                O000O00O00OOO0O0O ._loaded =True #line:34
                return True #line:35
            return False #line:36
        except :#line:37
            return False #line:38
    def _crop_image (O0O00O000O0OO00O0 ,OOO00OOOO0O00OOOO ):#line:40
        O00O000OOOOOOOO0O =OOO00OOOO0O00OOOO .shape [1 ]#line:41
        OOOO00OOO0OOO00O0 =OOO00OOOO0O00OOOO .shape [0 ]#line:42
        if OOOO00OOO0OOO00O0 >O00O000OOOOOOOO0O :#line:43
            if O0O00O000O0OO00O0 ._square =='left':#line:44
                OO0OO0O0OO000O0OO =0 #line:45
            elif O0O00O000O0OO00O0 ._square =='right':#line:46
                OO0OO0O0OO000O0OO =OOOO00OOO0OOO00O0 -O00O000OOOOOOOO0O #line:47
            else :#line:48
                OO0OO0O0OO000O0OO =(OOOO00OOO0OOO00O0 -O00O000OOOOOOOO0O )//2 #line:49
            OOO00OOOO0O00OOOO =OOO00OOOO0O00OOOO [OO0OO0O0OO000O0OO :OO0OO0O0OO000O0OO +O00O000OOOOOOOO0O ,:]#line:50
        else :#line:51
            if O0O00O000O0OO00O0 ._square =='left':#line:52
                OO0OO0O0OO000O0OO =0 #line:53
            elif O0O00O000O0OO00O0 ._square =='right':#line:54
                OO0OO0O0OO000O0OO =O00O000OOOOOOOO0O -OOOO00OOO0OOO00O0 #line:55
            else :#line:56
                OO0OO0O0OO000O0OO =(O00O000OOOOOOOO0O -OOOO00OOO0OOO00O0 )//2 #line:57
            OOO00OOOO0O00OOOO =OOO00OOOO0O00OOOO [:,OO0OO0O0OO000O0OO :OO0OO0O0OO000O0OO +OOOO00OOO0OOO00O0 ]#line:58
        return cv2 .resize (OOO00OOOO0O00OOOO ,dsize =(224 ,224 ))#line:59
    def predict (OOOO000OO0OO00O0O ,OO00O00O00O0O000O ,threshold =0.5 ,verbose =0 ):#line:61
        if OO00O00O00O0O000O is None :#line:62
            OOOO000OO0OO00O0O ._clear ()#line:63
        elif OOOO000OO0OO00O0O ._loaded :#line:64
            OO0OOOO00OOO0OOOO =OOOO000OO0OO00O0O ._crop_image (OO00O00O00O0O000O )#line:65
            OOOO000OO0OO00O0O ._data [0 ]=(OO0OOOO00OOO0OOOO .astype (np .float32 )/127.0 )-1 #line:66
            O00O0OOO00O0O0O0O =OOOO000OO0OO00O0O ._confidences =OOOO000OO0OO00O0O ._model .predict (OOOO000OO0OO00O0O ._data ,verbose =verbose )[0 ]#line:67
            if O00O0OOO00O0O0O0O .size >0 :#line:68
                OO00OO0000OO00O00 =O00O0OOO00O0O0O0O .argmax ()#line:69
                if O00O0OOO00O0O0O0O [OO00OO0000OO00O00 ]<threshold :#line:70
                    OOOO000OO0OO00O0O ._best_label =''#line:71
                    OOOO000OO0OO00O0O ._best_confidence =0 #line:72
                else :#line:73
                    OOOO000OO0OO00O0O ._best_label =OOOO000OO0OO00O0O ._labels [OO00OO0000OO00O00 ]#line:74
                    OOOO000OO0OO00O0O ._best_confidence =O00O0OOO00O0O0O0O [OO00OO0000OO00O00 ]#line:75
                    return True #line:76
        return False #line:77
    def set_square (O00OOO0O000O00O0O ,OO00OO00OO000OOOO ):#line:79
        if OO00OO00OO000OOOO is None :#line:80
            O00OOO0O000O00O0O ._square ='center'#line:81
        elif isinstance (OO00OO00OO000OOOO ,str ):#line:82
            O00OOO0O000O00O0O ._square =OO00OO00OO000OOOO .lower ()#line:83
    def draw_square (O00O000OOO0O0OOOO ,OOOO0O00000000OOO ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:85
        if OOOO0O00000000OOO is not None :#line:86
            if clone :#line:87
                OOOO0O00000000OOO =OOOO0O00000000OOO .copy ()#line:88
            O0O0O0OOO0000O00O =OOOO0O00000000OOO .shape [1 ]#line:89
            OO0O0000OOO0OO000 =OOOO0O00000000OOO .shape [0 ]#line:90
            if OO0O0000OOO0OO000 >O0O0O0OOO0000O00O :#line:91
                if O00O000OOO0O0OOOO ._square =='left':#line:92
                    O00OOOO00OO0OOOOO =0 #line:93
                elif O00O000OOO0O0OOOO ._square =='right':#line:94
                    O00OOOO00OO0OOOOO =OO0O0000OOO0OO000 -O0O0O0OOO0000O00O #line:95
                else :#line:96
                    O00OOOO00OO0OOOOO =(OO0O0000OOO0OO000 -O0O0O0OOO0000O00O )//2 #line:97
                cv2 .rectangle (OOOO0O00000000OOO ,(0 ,O00OOOO00OO0OOOOO ),(O0O0O0OOO0000O00O ,O00OOOO00OO0OOOOO +O0O0O0OOO0000O00O ),color ,thickness )#line:98
            else :#line:99
                if O00O000OOO0O0OOOO ._square =='left':#line:100
                    O00OOOO00OO0OOOOO =0 #line:101
                elif O00O000OOO0O0OOOO ._square =='right':#line:102
                    O00OOOO00OO0OOOOO =O0O0O0OOO0000O00O -OO0O0000OOO0OO000 #line:103
                else :#line:104
                    O00OOOO00OO0OOOOO =(O0O0O0OOO0000O00O -OO0O0000OOO0OO000 )//2 #line:105
                cv2 .rectangle (OOOO0O00000000OOO ,(O00OOOO00OO0OOOOO ,0 ),(O00OOOO00OO0OOOOO +OO0O0000OOO0OO000 ,OO0O0000OOO0OO000 ),color ,thickness )#line:106
        return OOOO0O00000000OOO #line:107
    def get_label (OO000OO0O0000O000 ):#line:109
        return OO000OO0O0000O000 ._best_label #line:110
    def get_conf (O00000000O00O0OO0 ):#line:112
        return O00000000O00O0OO0 ._best_confidence #line:113
    def get_all_labels (O0O0000O0OOO00000 ):#line:115
        return O0O0000O0OOO00000 ._labels #line:116
    def get_all_confs (O00OOO000O0OO00O0 ):#line:118
        return O00OOO000O0OO00O0 ._confidences #line:119
