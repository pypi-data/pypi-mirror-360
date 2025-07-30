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
    def __init__ (OO000O0000OO0O00O ,square ='center'):#line:9
        OO000O0000OO0O00O ._loaded =False #line:10
        OO000O0000OO0O00O ._model =None #line:11
        OO000O0000OO0O00O ._data =np .ndarray (shape =(1 ,224 ,224 ,3 ),dtype =np .float32 )#line:12
        OO000O0000OO0O00O .set_square (square )#line:13
        OO000O0000OO0O00O ._clear ()#line:14
    def _clear (OO0OO00OOO000OO00 ):#line:16
        OO0OO00OOO000OO00 ._best_label =''#line:17
        OO0OO00OOO000OO00 ._best_confidence =0 #line:18
        OO0OO00OOO000OO00 ._labels =[]#line:19
        OO0OO00OOO000OO00 ._confidences =[]#line:20
    def load_model (O0O0O00O0OOO00O0O ,OOOO0OO0OOOOOOO0O ):#line:22
        import os #line:23
        os .environ ["TF_USE_LEGACY_KERAS"]="1"#line:24
        import tensorflow as tf #line:25
        O0O0O00O0OOO00O0O ._loaded =False #line:26
        try :#line:27
            OO0O0OOO000O0000O =os .path .join (OOOO0OO0OOOOOOO0O ,'keras_model.h5')#line:28
            O000OOO0O0000OOOO =os .path .join (OOOO0OO0OOOOOOO0O ,'labels.txt')#line:29
            O0O0O00O0OOO00O0O ._model =tf .keras .models .load_model (OO0O0OOO000O0000O ,compile =False )#line:30
            with open (O000OOO0O0000OOOO ,'r',encoding ='utf8')as OO0O0O00OOOO0OO00 :#line:31
                O0O0O000O000OOO0O =OO0O0O00OOOO0OO00 .readlines ()#line:32
                O0O0O00O0OOO00O0O ._labels =np .array ([O00O0OOOO00OO0O0O [O00O0OOOO00OO0O0O .find (' ')+1 :].strip ()for O00O0OOOO00OO0O0O in O0O0O000O000OOO0O ])#line:33
                O0O0O00O0OOO00O0O ._loaded =True #line:34
                return True #line:35
            return False #line:36
        except :#line:37
            return False #line:38
    def _crop_image (O0OO0OO0OO00OOO00 ,O00O0OOOOOO0O0OO0 ):#line:40
        OO0O000O00OOOOOOO =O00O0OOOOOO0O0OO0 .shape [1 ]#line:41
        O00O00O0O0O00OOOO =O00O0OOOOOO0O0OO0 .shape [0 ]#line:42
        if O00O00O0O0O00OOOO >OO0O000O00OOOOOOO :#line:43
            if O0OO0OO0OO00OOO00 ._square =='left':#line:44
                OO0O0O0OOOOO00OO0 =0 #line:45
            elif O0OO0OO0OO00OOO00 ._square =='right':#line:46
                OO0O0O0OOOOO00OO0 =O00O00O0O0O00OOOO -OO0O000O00OOOOOOO #line:47
            else :#line:48
                OO0O0O0OOOOO00OO0 =(O00O00O0O0O00OOOO -OO0O000O00OOOOOOO )//2 #line:49
            O00O0OOOOOO0O0OO0 =O00O0OOOOOO0O0OO0 [OO0O0O0OOOOO00OO0 :OO0O0O0OOOOO00OO0 +OO0O000O00OOOOOOO ,:]#line:50
        else :#line:51
            if O0OO0OO0OO00OOO00 ._square =='left':#line:52
                OO0O0O0OOOOO00OO0 =0 #line:53
            elif O0OO0OO0OO00OOO00 ._square =='right':#line:54
                OO0O0O0OOOOO00OO0 =OO0O000O00OOOOOOO -O00O00O0O0O00OOOO #line:55
            else :#line:56
                OO0O0O0OOOOO00OO0 =(OO0O000O00OOOOOOO -O00O00O0O0O00OOOO )//2 #line:57
            O00O0OOOOOO0O0OO0 =O00O0OOOOOO0O0OO0 [:,OO0O0O0OOOOO00OO0 :OO0O0O0OOOOO00OO0 +O00O00O0O0O00OOOO ]#line:58
        return cv2 .resize (O00O0OOOOOO0O0OO0 ,dsize =(224 ,224 ))#line:59
    def predict (O000OO0O0O0O00OOO ,O0OO0O0O00OO000OO ,threshold =0.5 ,verbose =0 ):#line:61
        if O0OO0O0O00OO000OO is None :#line:62
            O000OO0O0O0O00OOO ._clear ()#line:63
        elif O000OO0O0O0O00OOO ._loaded :#line:64
            OOO0OOO0OOO000O00 =O000OO0O0O0O00OOO ._crop_image (O0OO0O0O00OO000OO )#line:65
            O000OO0O0O0O00OOO ._data [0 ]=(OOO0OOO0OOO000O00 .astype (np .float32 )/127.0 )-1 #line:66
            O0O0O00OOO0OO0O00 =O000OO0O0O0O00OOO ._confidences =O000OO0O0O0O00OOO ._model .predict (O000OO0O0O0O00OOO ._data ,verbose =verbose )[0 ]#line:67
            if O0O0O00OOO0OO0O00 .size >0 :#line:68
                OOOO0000OO000O0O0 =O0O0O00OOO0OO0O00 .argmax ()#line:69
                if O0O0O00OOO0OO0O00 [OOOO0000OO000O0O0 ]<threshold :#line:70
                    O000OO0O0O0O00OOO ._best_label =''#line:71
                    O000OO0O0O0O00OOO ._best_confidence =0 #line:72
                else :#line:73
                    O000OO0O0O0O00OOO ._best_label =O000OO0O0O0O00OOO ._labels [OOOO0000OO000O0O0 ]#line:74
                    O000OO0O0O0O00OOO ._best_confidence =O0O0O00OOO0OO0O00 [OOOO0000OO000O0O0 ]#line:75
                    return True #line:76
        return False #line:77
    def set_square (OOOOO0O0OO0OOO0OO ,O0OO0OOOO0OO000O0 ):#line:79
        if O0OO0OOOO0OO000O0 is None :#line:80
            OOOOO0O0OO0OOO0OO ._square ='center'#line:81
        elif isinstance (O0OO0OOOO0OO000O0 ,str ):#line:82
            OOOOO0O0OO0OOO0OO ._square =O0OO0OOOO0OO000O0 .lower ()#line:83
    def draw_square (OOO00OOO000O00O0O ,O0O000O0OO0O00O0O ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:85
        if O0O000O0OO0O00O0O is not None :#line:86
            if clone :#line:87
                O0O000O0OO0O00O0O =O0O000O0OO0O00O0O .copy ()#line:88
            O00OOOO0000O000OO =O0O000O0OO0O00O0O .shape [1 ]#line:89
            OOO00OO0OOOO00000 =O0O000O0OO0O00O0O .shape [0 ]#line:90
            if OOO00OO0OOOO00000 >O00OOOO0000O000OO :#line:91
                if OOO00OOO000O00O0O ._square =='left':#line:92
                    OO00OO0OO0O0000O0 =0 #line:93
                elif OOO00OOO000O00O0O ._square =='right':#line:94
                    OO00OO0OO0O0000O0 =OOO00OO0OOOO00000 -O00OOOO0000O000OO #line:95
                else :#line:96
                    OO00OO0OO0O0000O0 =(OOO00OO0OOOO00000 -O00OOOO0000O000OO )//2 #line:97
                cv2 .rectangle (O0O000O0OO0O00O0O ,(0 ,OO00OO0OO0O0000O0 ),(O00OOOO0000O000OO ,OO00OO0OO0O0000O0 +O00OOOO0000O000OO ),color ,thickness )#line:98
            else :#line:99
                if OOO00OOO000O00O0O ._square =='left':#line:100
                    OO00OO0OO0O0000O0 =0 #line:101
                elif OOO00OOO000O00O0O ._square =='right':#line:102
                    OO00OO0OO0O0000O0 =O00OOOO0000O000OO -OOO00OO0OOOO00000 #line:103
                else :#line:104
                    OO00OO0OO0O0000O0 =(O00OOOO0000O000OO -OOO00OO0OOOO00000 )//2 #line:105
                cv2 .rectangle (O0O000O0OO0O00O0O ,(OO00OO0OO0O0000O0 ,0 ),(OO00OO0OO0O0000O0 +OOO00OO0OOOO00000 ,OOO00OO0OOOO00000 ),color ,thickness )#line:106
        return O0O000O0OO0O00O0O #line:107
    def get_label (OO000O0OOO00OO00O ):#line:109
        return OO000O0OOO00OO00O ._best_label #line:110
    def get_conf (O00O0O0O0O00O0O0O ):#line:112
        return O00O0O0O0O00O0O0O ._best_confidence #line:113
    def get_all_labels (OOOOOOO0O0O0OO0OO ):#line:115
        return OOOOOOO0O0O0OO0OO ._labels #line:116
    def get_all_confs (OO0O0OO0OO00OO0OO ):#line:118
        return OO0O0OO0OO00OO0OO ._confidences #line:119
