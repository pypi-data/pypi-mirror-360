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
_OO0O0OO000O0OOO00 =None #line:4
def wait_until_fruit (OO0O0000000O0O0O0 ,OO00OOOOOOO0OOOO0 ,interval_msec =1 ,lang ='en'):#line:7
    global _OO0O0OO000O0OOO00 #line:8
    if _OO0O0OO000O0OOO00 is None :#line:10
        _OO0O0OO000O0OOO00 =ObjectDetector (True ,lang )#line:11
        _OO0O0OO000O0OOO00 .download_model ()#line:12
        _OO0O0OO000O0OOO00 .load_model ()#line:13
    if not isinstance (OO00OOOOOOO0OOOO0 ,(list ,tuple )):#line:14
        OO00OOOOOOO0OOOO0 =(OO00OOOOOOO0OOOO0 ,)#line:15
    O0O0OOO0O0O000O0O =None #line:17
    while O0O0OOO0O0O000O0O is None :#line:18
        OO000OOOO00O000OO =OO0O0000000O0O0O0 .read ()#line:19
        if _OO0O0OO000O0OOO00 .detect (OO000OOOO00O000OO ):#line:20
            OO000OOOO00O000OO =_OO0O0OO000O0OOO00 .draw_result (OO000OOOO00O000OO )#line:21
            for OOOO0OOOOOO000OOO in OO00OOOOOOO0OOOO0 :#line:22
                if OOOO0OOOOOO000OOO in _OO0O0OO000O0OOO00 .get_label ():#line:23
                    O0O0OOO0O0O000O0O =OOOO0OOOOOO000OOO #line:24
                    break #line:25
        OO0O0000000O0O0O0 .show (OO000OOOO00O000OO )#line:26
        if OO0O0000000O0O0O0 .check_key (interval_msec )=='esc':break #line:27
    OO0O0000000O0O0O0 .hide ()#line:28
    return O0O0OOO0O0O000O0O #line:29
