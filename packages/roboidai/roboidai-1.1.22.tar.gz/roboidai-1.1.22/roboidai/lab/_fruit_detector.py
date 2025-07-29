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

from roboidai ._image ._object_detector import ObjectDetector #line:2
_OO0OOO000000O0OO0 =None #line:4
def wait_until_fruit (OOOO0OO0OOOO0000O ,OOO000OO0OOO00000 ,interval_msec =1 ,lang ='en'):#line:7
    global _OO0OOO000000O0OO0 #line:8
    if _OO0OOO000000O0OO0 is None :#line:10
        _OO0OOO000000O0OO0 =ObjectDetector (True ,lang )#line:11
        _OO0OOO000000O0OO0 .download_model ()#line:12
        _OO0OOO000000O0OO0 .load_model ()#line:13
    if not isinstance (OOO000OO0OOO00000 ,(list ,tuple )):#line:14
        OOO000OO0OOO00000 =(OOO000OO0OOO00000 ,)#line:15
    O00000O000000OO00 =None #line:17
    while O00000O000000OO00 is None :#line:18
        OO00O0O00O0OO0OO0 =OOOO0OO0OOOO0000O .read ()#line:19
        if _OO0OOO000000O0OO0 .detect (OO00O0O00O0OO0OO0 ):#line:20
            OO00O0O00O0OO0OO0 =_OO0OOO000000O0OO0 .draw_result (OO00O0O00O0OO0OO0 )#line:21
            for OOO00OO00O000O000 in OOO000OO0OOO00000 :#line:22
                if OOO00OO00O000O000 in _OO0OOO000000O0OO0 .get_label ():#line:23
                    O00000O000000OO00 =OOO00OO00O000O000 #line:24
                    break #line:25
        OOOO0OO0OOOO0000O .show (OO00O0O00O0OO0OO0 )#line:26
        if OOOO0OO0OOOO0000O .check_key (interval_msec )=='esc':break #line:27
    OOOO0OO0OOOO0000O .hide ()#line:28
    return O00000O000000OO00 #line:29
