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
    def distance (O0O000OO00O0O0O00 ,O000O0OOO00OO0000 ):#line:8
        if O0O000OO00O0O0O00 is not None and O000O0OOO00OO0000 is not None :#line:9
            O00O00000O0O00000 =min (len (O0O000OO00O0O0O00 ),len (O000O0OOO00OO0000 ))#line:10
            O00OO000OO0O00000 =0 #line:11
            for OO00OO0000O0OOO00 in range (O00O00000O0O00000 ):#line:12
                O00OO000OO0O00000 +=(O0O000OO00O0O0O00 [OO00OO0000O0OOO00 ]-O000O0OOO00OO0000 [OO00OO0000O0OOO00 ])**2 #line:13
            return math .sqrt (O00OO000OO0O00000 )#line:14
        return None #line:15
    @staticmethod #line:17
    def degree (O0OOOO00O00O0O00O ,O0O0O0O00OO0O0O0O ):#line:18
        if O0OOOO00O00O0O00O is not None and O0O0O0O00OO0O0O0O is not None :#line:19
            O0OOOOOOO000O0O0O =O0O0O0O00OO0O0O0O [0 ]-O0OOOO00O00O0O00O [0 ]#line:20
            OO0O0O0OOOOO0O0OO =O0OOOO00O00O0O00O [1 ]-O0O0O0O00OO0O0O0O [1 ]#line:21
            return math .degrees (math .atan2 (OO0O0O0OOOOO0O0OO ,O0OOOOOOO000O0O0O ))#line:22
        return None #line:23
    @staticmethod #line:25
    def radian (O00O0000OOOO00OOO ,O00OO0OO0000O000O ):#line:26
        if O00O0000OOOO00OOO is not None and O00OO0OO0000O000O is not None :#line:27
            OO0000O0OO0O00O00 =O00OO0OO0000O000O [0 ]-O00O0000OOOO00OOO [0 ]#line:28
            O0O0O0000OOO000O0 =O00O0000OOOO00OOO [1 ]-O00OO0OO0000O000O [1 ]#line:29
            return math .atan2 (O0O0O0000OOO000O0 ,OO0000O0OO0O00O00 )#line:30
        return None #line:31
    @staticmethod #line:33
    def realize_filepath (O0O0O0OO000OO000O ):#line:34
        if isinstance (O0O0O0OO000OO000O ,str ):#line:35
            OO0O0000OOO00OO00 =os .path .dirname (O0O0O0OO000OO000O )#line:36
            if not os .path .isdir (OO0O0000OOO00OO00 ):#line:37
                os .makedirs (OO0O0000OOO00OO00 )#line:38
class FontUtil :#line:41
    _FONT =None #line:42
    @staticmethod #line:44
    def get_font ():#line:45
        if FontUtil ._FONT is None :#line:46
            from PIL import ImageFont #line:47
            FontUtil ._FONT =ImageFont .truetype (os .sep .join ([os .path .dirname (os .path .realpath (__file__ )),'malgun.ttf']),12 )#line:48
        return FontUtil ._FONT #line:49
