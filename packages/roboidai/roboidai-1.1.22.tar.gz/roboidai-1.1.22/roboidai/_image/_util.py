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

import math #line:2
import os #line:3
class Util :#line:6
    @staticmethod #line:7
    def distance (O000O0OO00O00O0OO ,O00OO0OO0OO0O00OO ):#line:8
        if O000O0OO00O00O0OO is not None and O00OO0OO0OO0O00OO is not None :#line:9
            OOO000O0O0O0O0O00 =min (len (O000O0OO00O00O0OO ),len (O00OO0OO0OO0O00OO ))#line:10
            O0OO0OOOOO0OOOOO0 =0 #line:11
            for O00OOOOOOO00O0000 in range (OOO000O0O0O0O0O00 ):#line:12
                O0OO0OOOOO0OOOOO0 +=(O000O0OO00O00O0OO [O00OOOOOOO00O0000 ]-O00OO0OO0OO0O00OO [O00OOOOOOO00O0000 ])**2 #line:13
            return math .sqrt (O0OO0OOOOO0OOOOO0 )#line:14
        return None #line:15
    @staticmethod #line:17
    def degree (O0OO0O00OOO000000 ,O00000000O0000O0O ):#line:18
        if O0OO0O00OOO000000 is not None and O00000000O0000O0O is not None :#line:19
            OOOO0O00O0OO0000O =O00000000O0000O0O [0 ]-O0OO0O00OOO000000 [0 ]#line:20
            O0OOOO0O0O0OOO0OO =O0OO0O00OOO000000 [1 ]-O00000000O0000O0O [1 ]#line:21
            return math .degrees (math .atan2 (O0OOOO0O0O0OOO0OO ,OOOO0O00O0OO0000O ))#line:22
        return None #line:23
    @staticmethod #line:25
    def radian (OOO0O0O0OO0OO0OO0 ,OO00OOOO0OO00OO0O ):#line:26
        if OOO0O0O0OO0OO0OO0 is not None and OO00OOOO0OO00OO0O is not None :#line:27
            OOOOOOO00OOO0OO00 =OO00OOOO0OO00OO0O [0 ]-OOO0O0O0OO0OO0OO0 [0 ]#line:28
            OO0000O000O000O00 =OOO0O0O0OO0OO0OO0 [1 ]-OO00OOOO0OO00OO0O [1 ]#line:29
            return math .atan2 (OO0000O000O000O00 ,OOOOOOO00OOO0OO00 )#line:30
        return None #line:31
    @staticmethod #line:33
    def realize_filepath (O0OOOOO0O00000OO0 ):#line:34
        if isinstance (O0OOOOO0O00000OO0 ,str ):#line:35
            OO0000OOO0O0O000O =os .path .dirname (O0OOOOO0O00000OO0 )#line:36
            if not os .path .isdir (OO0000OOO0O0O000O ):#line:37
                os .makedirs (OO0000OOO0O0O000O )#line:38
class FontUtil :#line:41
    _FONT =None #line:42
    @staticmethod #line:44
    def get_font ():#line:45
        if FontUtil ._FONT is None :#line:46
            from PIL import ImageFont #line:47
            FontUtil ._FONT =ImageFont .truetype (os .sep .join ([os .path .dirname (os .path .realpath (__file__ )),'malgun.ttf']),12 )#line:48
        return FontUtil ._FONT #line:49
