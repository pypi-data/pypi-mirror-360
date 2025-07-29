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
class BodySegmentation :#line:7
    def __init__ (O000O00OO0OOOOOOO ):#line:8
        O000O00OO0OOOOOOO ._loaded =False #line:9
        O000O00OO0OOOOOOO ._condition =None #line:10
        O000O00OO0OOOOOOO ._bg_image =None #line:11
        O000O00OO0OOOOOOO ._bg_color =None #line:12
        O000O00OO0OOOOOOO ._bg_temp =None #line:13
    def load_model (OOOO000O0OO00OO0O ,model =0 ):#line:15
        try :#line:16
            OOOO000O0OO00OO0O ._segmentation =mp .solutions .selfie_segmentation .SelfieSegmentation (model_selection =model )#line:17
            OOOO000O0OO00OO0O ._loaded =True #line:18
            return True #line:19
        except :#line:20
            return False #line:21
    def _fit_to (OO0O00OOOO0000OO0 ,OOOO000O0O0O00OO0 ,OOO000000000O00OO ,OOO0O00OOOO000O00 ):#line:23
        if OOOO000O0O0O00OO0 is not None :#line:24
            OOOO0O00O0O0OO000 =OOOO000O0O0O00OO0 .shape [1 ]#line:25
            OOOO000O0O0OO0O0O =OOOO000O0O0O00OO0 .shape [0 ]#line:26
            if OOOO0O00O0O0OO000 ==OOO000000000O00OO and OOOO000O0O0OO0O0O ==OOO0O00OOOO000O00 :#line:27
                return OOOO000O0O0O00OO0 #line:28
            O0OOO0OOOO0O00O0O =OOOO0O00O0O0OO000 /OOOO000O0O0OO0O0O #line:29
            O0000O0000OOO0OOO =OOO000000000O00OO /OOO0O00OOOO000O00 #line:30
            if O0000O0000OOO0OOO >O0OOO0OOOO0O00O0O :#line:31
                OOOO000O0O0OO0O0O =int (OOO000000000O00OO *OOOO000O0O0OO0O0O /OOOO0O00O0O0OO000 )#line:32
                OOOO000O0O0O00OO0 =cv2 .resize (OOOO000O0O0O00OO0 ,(OOO000000000O00OO ,OOOO000O0O0OO0O0O ))#line:33
                O0OO00OOOOOO00O00 =(OOOO000O0O0OO0O0O -OOO0O00OOOO000O00 )//2 #line:34
                OOOO000O0O0O00OO0 =OOOO000O0O0O00OO0 [O0OO00OOOOOO00O00 :O0OO00OOOOOO00O00 +OOO0O00OOOO000O00 ,:]#line:35
            else :#line:36
                OOOO0O00O0O0OO000 =int (OOO0O00OOOO000O00 *OOOO0O00O0O0OO000 /OOOO000O0O0OO0O0O )#line:37
                OOOO000O0O0O00OO0 =cv2 .resize (OOOO000O0O0O00OO0 ,(OOOO0O00O0O0OO000 ,OOO0O00OOOO000O00 ))#line:38
                O0OO00OOOOOO00O00 =(OOOO0O00O0O0OO000 -OOO000000000O00OO )//2 #line:39
                OOOO000O0O0O00OO0 =OOOO000O0O0O00OO0 [:,O0OO00OOOOOO00O00 :O0OO00OOOOOO00O00 +OOO000000000O00OO ]#line:40
        return OOOO000O0O0O00OO0 #line:41
    def set_background (OOO00OOO00O0O0O0O ,O0OOO0O0OOO0OOOOO ,arg2 =None ,arg3 =None ):#line:43
        if isinstance (O0OOO0O0OOO0OOOOO ,str ):#line:44
            O0000O000O0OO0000 =cv2 .imread (O0OOO0O0OOO0OOOOO )#line:45
            if O0000O000O0OO0000 is None :#line:46
                try :#line:47
                    O0000O000O0OO0000 =np .fromfile (O0OOO0O0OOO0OOOOO ,np .uint8 )#line:48
                    OOO00OOO00O0O0O0O ._bg_image =cv2 .imdecode (O0000O000O0OO0000 ,cv2 .IMREAD_COLOR )#line:49
                except :#line:50
                    OOO00OOO00O0O0O0O ._bg_image =None #line:51
            else :#line:52
                OOO00OOO00O0O0O0O ._bg_image =O0000O000O0OO0000 #line:53
            OOO00OOO00O0O0O0O ._bg_color =None #line:54
        elif isinstance (O0OOO0O0OOO0OOOOO ,(int ,float )):#line:55
            if isinstance (arg2 ,(int ,float ))and isinstance (arg3 ,(int ,float )):#line:56
                OOO00OOO00O0O0O0O ._bg_image =None #line:57
                OOO00OOO00O0O0O0O ._bg_color =(int (arg3 ),int (arg2 ),int (O0OOO0O0OOO0OOOOO ))#line:58
        else :#line:59
            OOO00OOO00O0O0O0O ._bg_image =O0OOO0O0OOO0OOOOO #line:60
            OOO00OOO00O0O0O0O ._bg_color =None #line:61
    def process (OO00O00O00OOO00OO ,OOO00O0O0O00OO000 ):#line:63
        if OOO00O0O0O00OO000 is not None and OO00O00O00OOO00OO ._loaded :#line:64
            OOO00O0O0O00OO000 =cv2 .cvtColor (OOO00O0O0O00OO000 ,cv2 .COLOR_BGR2RGB )#line:65
            OOO00O0O0O00OO000 .flags .writeable =False #line:66
            OO0O00OO0O000OOOO =OO00O00O00OOO00OO ._segmentation .process (OOO00O0O0O00OO000 )#line:67
            if OO0O00OO0O000OOOO and OO0O00OO0O000OOOO .segmentation_mask is not None :#line:68
                OO00O00O00OOO00OO ._condition =np .stack ((OO0O00OO0O000OOOO .segmentation_mask ,)*3 ,axis =-1 )>0.1 #line:69
                return True #line:70
        OO00O00O00OOO00OO ._condition =None #line:71
        return False #line:72
    def _get_background (O0OO0O0O0OOO0OOOO ,OO00O0000O00O0O00 ,OOOO0OOOOO0OO00O0 ):#line:74
        if O0OO0O0O0OOO0OOOO ._bg_temp is None :#line:75
            O0OO0O0O0OOO0OOOO ._bg_temp =np .zeros (OO00O0000O00O0O00 ,dtype =np .uint8 )#line:76
        elif O0OO0O0O0OOO0OOOO ._bg_temp .shape [0 ]!=OO00O0000O00O0O00 [0 ]or O0OO0O0O0OOO0OOOO ._bg_temp .shape [1 ]!=OO00O0000O00O0O00 [1 ]:#line:77
            O0OO0O0O0OOO0OOOO ._bg_temp =np .zeros (OO00O0000O00O0O00 ,dtype =np .uint8 )#line:78
        if OOOO0OOOOO0OO00O0 is None :#line:79
            OOOO0OOOOO0OO00O0 =(0 ,0 ,0 )#line:80
        O0OO0O0O0OOO0OOOO ._bg_temp [:]=OOOO0OOOOO0OO00O0 #line:81
        return O0OO0O0O0OOO0OOOO ._bg_temp #line:82
    def draw_result (OOOOO000O0OOO000O ,O0OOOO0O00O0O0OO0 ):#line:84
        if O0OOOO0O00O0O0OO0 is not None and OOOOO000O0OOO000O ._condition is not None :#line:85
            if OOOOO000O0OOO000O ._bg_image is not None :#line:86
                OO0O0O0OOOOOO0OO0 =OOOOO000O0OOO000O ._fit_to (OOOOO000O0OOO000O ._bg_image ,O0OOOO0O00O0O0OO0 .shape [1 ],O0OOOO0O00O0O0OO0 .shape [0 ])#line:87
            else :#line:88
                OO0O0O0OOOOOO0OO0 =OOOOO000O0OOO000O ._get_background (O0OOOO0O00O0O0OO0 .shape ,OOOOO000O0OOO000O ._bg_color )#line:89
            O0OOOO0O00O0O0OO0 =np .where (OOOOO000O0OOO000O ._condition ,O0OOOO0O00O0O0OO0 ,OO0O0O0OOOOOO0OO0 )#line:90
        return O0OOOO0O00O0O0OO0 #line:91
