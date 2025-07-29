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
def find_track_xy (OO00OO0OOO00O0000 ,OO0OO00OOO0OO0O0O ,O000OOOO0O0O0OO0O ,OO0OOOOOOO00O00O0 ,s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:6
    OOO00OOOOO0O00O00 =OO00OO0OOO00O0000 .shape [1 ]#line:7
    OOO0000000OOO0000 =OO00OO0OOO00O0000 .shape [0 ]#line:8
    OOO000O00OO0OO000 =0 if window_height <0 else OOO0000000OOO0000 -window_height #line:9
    OO0O0000OO0OO000O =OO00OO0OOO00O0000 [OOO000O00OO0OO000 :OOO0000000OOO0000 ,:]#line:11
    OOOOOOOO0OO000000 =cv2 .cvtColor (OO0O0000OO0OO000O ,cv2 .COLOR_BGR2HSV )#line:12
    OOO0OOOOOOOOO0O0O =cv2 .inRange (OOOOOOOO0OO000000 ,(OO0OOOOOOO00O00O0 [0 ],s_range [0 ],v_range [0 ]),(OO0OOOOOOO00O00O0 [1 ],s_range [1 ],v_range [1 ]))#line:14
    if len (OO0OOOOOOO00O00O0 )>=4 :#line:15
        OOO0OOOOOOOOO0O0O |=cv2 .inRange (OOOOOOOO0OO000000 ,(OO0OOOOOOO00O00O0 [2 ],s_range [0 ],v_range [0 ]),(OO0OOOOOOO00O00O0 [3 ],s_range [1 ],v_range [1 ]))#line:16
    OOOO0O000O000O000 =np .ones ((3 ,3 ),np .uint8 )#line:18
    OOO0OOOOOOOOO0O0O =cv2 .morphologyEx (OOO0OOOOOOOOO0O0O ,cv2 .MORPH_OPEN ,OOOO0O000O000O000 )#line:19
    OOO0OOOOOOOOO0O0O =cv2 .morphologyEx (OOO0OOOOOOOOO0O0O ,cv2 .MORPH_CLOSE ,OOOO0O000O000O000 )#line:20
    OOO0O0O0O0O00O000 ,_O0O0000OOOO0OOOOO =cv2 .findContours (OOO0OOOOOOOOO0O0O ,cv2 .RETR_LIST ,cv2 .CHAIN_APPROX_SIMPLE )#line:22
    OO0OOOOOOO000O0OO =[cv2 .contourArea (O0000OOO00O00OO0O )for O0000OOO00O00OO0O in OOO0O0O0O0O00O000 ]#line:23
    if OO0OOOOOOO000O0OO :#line:24
        OO000O0OO00OOOO00 =np .argmax (OO0OOOOOOO000O0OO )#line:25
        OO0O00OOOOO0O0O0O =OO0OOOOOOO000O0OO [OO000O0OO00OOOO00 ]#line:26
        if OO0O00OOOOO0O0O0O >min_area :#line:27
            OO0OOO0OOO0OOO0O0 =OOO0O0O0O0O00O000 [OO000O0OO00OOOO00 ]#line:28
            cv2 .drawContours (OO0OO00OOO0OO0O0O ,OOO0O0O0O0O00O000 ,OO000O0OO00OOOO00 ,O000OOOO0O0O0OO0O ,-1 ,offset =(0 ,OOO000O00OO0OO000 ))#line:29
            OOO00O0O00O0000OO =cv2 .moments (OO0OOO0OOO0OOO0O0 )#line:30
            OOO0OO00O00OOO0O0 =OOO00O0O00O0000OO ['m00']#line:31
            if OOO0OO00O00OOO0O0 >0 :#line:32
                return int (OOO00O0O00O0000OO ['m10']/OOO0OO00O00OOO0O0 ),int (OOO00O0O00O0000OO ['m01']/OOO0OO00O00OOO0O0 )#line:33
    return -1 ,-1 #line:34
def find_green_track_xy (O0OO0000OOO00O0OO ,O000OO00O0OO0000O ,h_range =(40 ,80 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:37
    return find_track_xy (O0OO0000OOO00O0OO ,O000OO00O0OO0000O ,(0 ,255 ,0 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:38
def find_blue_track_xy (O00O0OO0O0OO00OO0 ,OOO000O0O0OO0O00O ,h_range =(100 ,140 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:41
    return find_track_xy (O00O0OO0O0OO00OO0 ,OOO000O0O0OO0O00O ,(255 ,0 ,0 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:42
def find_red_track_xy (OO0O00O0O0O0OOO00 ,OOO00O00O0O00O00O ,h_range =(0 ,10 ,170 ,180 ),s_range =(50 ,255 ),v_range =(50 ,255 ),window_height =-1 ,min_area =0 ):#line:45
    return find_track_xy (OO0O00O0O0O0OOO00 ,OOO00O00O0O00O00O ,(0 ,0 ,255 ),h_range ,s_range ,v_range ,window_height ,min_area )#line:46
