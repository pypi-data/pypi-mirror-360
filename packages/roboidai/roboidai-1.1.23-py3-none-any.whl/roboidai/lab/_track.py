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
def find_track_xy (O00OOOO0O000O0O0O ,OOOOOOO0000OO000O ,O0OOOO0O000000OO0 ,OO0O000O0OOOOO00O ,s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:6
    O00O00O0OOO000OO0 =O00OOOO0O000O0O0O .shape [1 ]#line:7
    OO0O0OO000O0OOOO0 =O00OOOO0O000O0O0O .shape [0 ]#line:8
    OOOO000000O000OO0 =0 if window_height <0 else OO0O0OO000O0OOOO0 -window_height #line:9
    OOOOO0O00000OOOOO =O00OOOO0O000O0O0O [OOOO000000O000OO0 :OO0O0OO000O0OOOO0 ,:]#line:11
    O00OO0O0OO0000O0O =cv2 .cvtColor (OOOOO0O00000OOOOO ,cv2 .COLOR_BGR2HSV )#line:12
    OO0O0O00OO00O000O =cv2 .inRange (O00OO0O0OO0000O0O ,(OO0O000O0OOOOO00O [0 ],s_range [0 ],v_range [0 ]),(OO0O000O0OOOOO00O [1 ],s_range [1 ],v_range [1 ]))#line:14
    if len (OO0O000O0OOOOO00O )>=4 :#line:15
        OO0O0O00OO00O000O |=cv2 .inRange (O00OO0O0OO0000O0O ,(OO0O000O0OOOOO00O [2 ],s_range [0 ],v_range [0 ]),(OO0O000O0OOOOO00O [3 ],s_range [1 ],v_range [1 ]))#line:16
    OO0O00OO0O00O000O =np .ones ((3 ,3 ),np .uint8 )#line:18
    OO0O0O00OO00O000O =cv2 .morphologyEx (OO0O0O00OO00O000O ,cv2 .MORPH_OPEN ,OO0O00OO0O00O000O )#line:19
    OO0O0O00OO00O000O =cv2 .morphologyEx (OO0O0O00OO00O000O ,cv2 .MORPH_CLOSE ,OO0O00OO0O00O000O )#line:20
    O0OO00O000O0OOO0O ,_O000OOOOOOOO0000O =cv2 .findContours (OO0O0O00OO00O000O ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:22
    OOO0OOOO000O0000O =[cv2 .contourArea (O000O0O0OO00OO00O )for O000O0O0OO00OO00O in O0OO00O000O0OOO0O ]#line:23
    if OOO0OOOO000O0000O :#line:24
        O000000OO0OOO0OOO =np .argmax (OOO0OOOO000O0000O )#line:25
        O00000O00O0OOO0OO =OOO0OOOO000O0000O [O000000OO0OOO0OOO ]#line:26
        if O00000O00O0OOO0OO >min_area :#line:27
            OOOOOOOOO0O0O0000 =O0OO00O000O0OOO0O [O000000OO0OOO0OOO ]#line:28
            cv2 .drawContours (OOOOOOO0000OO000O ,O0OO00O000O0OOO0O ,O000000OO0OOO0OOO ,O0OOOO0O000000OO0 ,-1 ,offset =(0 ,OOOO000000O000OO0 ))#line:29
            O0OOOOO00OOOOO0O0 =cv2 .moments (OOOOOOOOO0O0O0000 )#line:30
            OOOOO0OO000O0OO0O =O0OOOOO00OOOOO0O0 ['m00']#line:31
            if OOOOO0OO000O0OO0O >0 :#line:32
                return int (O0OOOOO00OOOOO0O0 ['m10']/OOOOO0OO000O0OO0O ),int (O0OOOOO00OOOOO0O0 ['m01']/OOOOO0OO000O0OO0O )#line:33
    return -1 ,-1 #line:34
def find_green_track_xy (O00O0O00OOO0O000O ,OO00OOO0O00O00O0O ,h_range =(40 ,80 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:37
    return find_track_xy (O00O0O00OOO0O000O ,OO00OOO0O00O00O0O ,(0 ,255 ,0 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:38
def find_blue_track_xy (OOOO0O00000OOO0OO ,O0000O0OO000OO0O0 ,h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:41
    return find_track_xy (OOOO0O00000OOO0OO ,O0000O0OO000OO0O0 ,(255 ,0 ,0 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:42
def find_red_track_xy (OOOOOO0O0OOO00OO0 ,OOO0O0OO00O0OO00O ,h_range =(0 ,10 ,170 ,180 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:45
    return find_track_xy (OOOOOO0O0OOO00OO0 ,OOO0O0OO00O0OO00O ,(0 ,0 ,255 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:46
