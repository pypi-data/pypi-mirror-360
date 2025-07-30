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
    def __init__ (O0O0000OOOO0OOO00 ):#line:8
        O0O0000OOOO0OOO00 ._loaded =False #line:9
        O0O0000OOOO0OOO00 ._condition =None #line:10
        O0O0000OOOO0OOO00 ._bg_image =None #line:11
        O0O0000OOOO0OOO00 ._bg_color =None #line:12
        O0O0000OOOO0OOO00 ._bg_temp =None #line:13
    def load_model (O000000OO00OOO0O0 ,model =0 ):#line:15
        try :#line:16
            O000000OO00OOO0O0 ._segmentation =mp .solutions .selfie_segmentation .SelfieSegmentation (model_selection =model )#line:17
            O000000OO00OOO0O0 ._loaded =True #line:18
            return True #line:19
        except :#line:20
            return False #line:21
    def _fit_to (O0OO0OO00OOOO0O00 ,O0OO0OOOO000O0OOO ,OO0O0OOO0O0O000O0 ,OOO0OOO00O0O0O000 ):#line:23
        if O0OO0OOOO000O0OOO is not None :#line:24
            OOO0O00OO00OOO0O0 =O0OO0OOOO000O0OOO .shape [1 ]#line:25
            O00O0000O0OOOOOO0 =O0OO0OOOO000O0OOO .shape [0 ]#line:26
            if OOO0O00OO00OOO0O0 ==OO0O0OOO0O0O000O0 and O00O0000O0OOOOOO0 ==OOO0OOO00O0O0O000 :#line:27
                return O0OO0OOOO000O0OOO #line:28
            O0OO0OO00OO000OO0 =OOO0O00OO00OOO0O0 /O00O0000O0OOOOOO0 #line:29
            OOO000000O000O00O =OO0O0OOO0O0O000O0 /OOO0OOO00O0O0O000 #line:30
            if OOO000000O000O00O >O0OO0OO00OO000OO0 :#line:31
                O00O0000O0OOOOOO0 =int (OO0O0OOO0O0O000O0 *O00O0000O0OOOOOO0 /OOO0O00OO00OOO0O0 )#line:32
                O0OO0OOOO000O0OOO =cv2 .resize (O0OO0OOOO000O0OOO ,(OO0O0OOO0O0O000O0 ,O00O0000O0OOOOOO0 ))#line:33
                O00OOOOOOOOOO000O =(O00O0000O0OOOOOO0 -OOO0OOO00O0O0O000 )//2 #line:34
                O0OO0OOOO000O0OOO =O0OO0OOOO000O0OOO [O00OOOOOOOOOO000O :O00OOOOOOOOOO000O +OOO0OOO00O0O0O000 ,:]#line:35
            else :#line:36
                OOO0O00OO00OOO0O0 =int (OOO0OOO00O0O0O000 *OOO0O00OO00OOO0O0 /O00O0000O0OOOOOO0 )#line:37
                O0OO0OOOO000O0OOO =cv2 .resize (O0OO0OOOO000O0OOO ,(OOO0O00OO00OOO0O0 ,OOO0OOO00O0O0O000 ))#line:38
                O00OOOOOOOOOO000O =(OOO0O00OO00OOO0O0 -OO0O0OOO0O0O000O0 )//2 #line:39
                O0OO0OOOO000O0OOO =O0OO0OOOO000O0OOO [:,O00OOOOOOOOOO000O :O00OOOOOOOOOO000O +OO0O0OOO0O0O000O0 ]#line:40
        return O0OO0OOOO000O0OOO #line:41
    def set_background (O00OOO00OOOOOO000 ,O000OO0O0OOOO0OOO ,arg2 =None ,arg3 =None ):#line:43
        if isinstance (O000OO0O0OOOO0OOO ,str ):#line:44
            OO00O0000O0000O0O =cv2 .imread (O000OO0O0OOOO0OOO )#line:45
            if OO00O0000O0000O0O is None :#line:46
                try :#line:47
                    OO00O0000O0000O0O =np .fromfile (O000OO0O0OOOO0OOO ,np .uint8 )#line:48
                    O00OOO00OOOOOO000 ._bg_image =cv2 .imdecode (OO00O0000O0000O0O ,cv2 .IMREAD_COLOR )#line:49
                except :#line:50
                    O00OOO00OOOOOO000 ._bg_image =None #line:51
            else :#line:52
                O00OOO00OOOOOO000 ._bg_image =OO00O0000O0000O0O #line:53
            O00OOO00OOOOOO000 ._bg_color =None #line:54
        elif isinstance (O000OO0O0OOOO0OOO ,(int ,float )):#line:55
            if isinstance (arg2 ,(int ,float ))and isinstance (arg3 ,(int ,float )):#line:56
                O00OOO00OOOOOO000 ._bg_image =None #line:57
                O00OOO00OOOOOO000 ._bg_color =(int (arg3 ),int (arg2 ),int (O000OO0O0OOOO0OOO ))#line:58
        else :#line:59
            O00OOO00OOOOOO000 ._bg_image =O000OO0O0OOOO0OOO #line:60
            O00OOO00OOOOOO000 ._bg_color =None #line:61
    def process (O00O00000OO0O0O0O ,O0OO0000O0000OOOO ):#line:63
        if O0OO0000O0000OOOO is not None and O00O00000OO0O0O0O ._loaded :#line:64
            O0OO0000O0000OOOO =cv2 .cvtColor (O0OO0000O0000OOOO ,cv2 .COLOR_BGR2RGB )#line:65
            O0OO0000O0000OOOO .flags .writeable =False #line:66
            O0000000O0OOO0O0O =O00O00000OO0O0O0O ._segmentation .process (O0OO0000O0000OOOO )#line:67
            if O0000000O0OOO0O0O and O0000000O0OOO0O0O .segmentation_mask is not None :#line:68
                O00O00000OO0O0O0O ._condition =np .stack ((O0000000O0OOO0O0O .segmentation_mask ,)*3 ,axis =-1 )>0.1 #line:69
                return True #line:70
        O00O00000OO0O0O0O ._condition =None #line:71
        return False #line:72
    def _get_background (OOO0O0000O0O00OO0 ,OOOOO0O0O0OOOOOO0 ,OOO00O000O0OOO0O0 ):#line:74
        if OOO0O0000O0O00OO0 ._bg_temp is None :#line:75
            OOO0O0000O0O00OO0 ._bg_temp =np .zeros (OOOOO0O0O0OOOOOO0 ,dtype =np .uint8 )#line:76
        elif OOO0O0000O0O00OO0 ._bg_temp .shape [0 ]!=OOOOO0O0O0OOOOOO0 [0 ]or OOO0O0000O0O00OO0 ._bg_temp .shape [1 ]!=OOOOO0O0O0OOOOOO0 [1 ]:#line:77
            OOO0O0000O0O00OO0 ._bg_temp =np .zeros (OOOOO0O0O0OOOOOO0 ,dtype =np .uint8 )#line:78
        if OOO00O000O0OOO0O0 is None :#line:79
            OOO00O000O0OOO0O0 =(0 ,0 ,0 )#line:80
        OOO0O0000O0O00OO0 ._bg_temp [:]=OOO00O000O0OOO0O0 #line:81
        return OOO0O0000O0O00OO0 ._bg_temp #line:82
    def draw_result (O00000O00O0O0OO00 ,O00O000O000O0OO00 ):#line:84
        if O00O000O000O0OO00 is not None and O00000O00O0O0OO00 ._condition is not None :#line:85
            if O00000O00O0O0OO00 ._bg_image is not None :#line:86
                O00OO00OOOOO0OOO0 =O00000O00O0O0OO00 ._fit_to (O00000O00O0O0OO00 ._bg_image ,O00O000O000O0OO00 .shape [1 ],O00O000O000O0OO00 .shape [0 ])#line:87
            else :#line:88
                O00OO00OOOOO0OOO0 =O00000O00O0O0OO00 ._get_background (O00O000O000O0OO00 .shape ,O00000O00O0O0OO00 ._bg_color )#line:89
            O00O000O000O0OO00 =np .where (O00000O00O0O0OO00 ._condition ,O00O000O000O0OO00 ,O00OO00OOOOO0OOO0 )#line:90
        return O00O000O000O0OO00 #line:91
