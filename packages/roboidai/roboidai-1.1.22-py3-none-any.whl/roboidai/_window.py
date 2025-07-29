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

from roboid import Runner #line:2
import cv2 #line:3
_O0OO000O0O00O00O0 ={8 :'bs',9 :'tab',13 :'enter',27 :'esc'}#line:11
_OOO00O0O00O0O0000 ={'bs':8 ,'tab':9 ,'enter':13 ,'esc':27 }#line:17
class Window :#line:20
    @staticmethod #line:21
    def check_key (timeout_msec =1 ):#line:22
        OO000OOO00000O0O0 =cv2 .waitKey (timeout_msec )#line:23
        if OO000OOO00000O0O0 >=32 and OO000OOO00000O0O0 <=126 :return chr (OO000OOO00000O0O0 )#line:24
        elif OO000OOO00000O0O0 in _O0OO000O0O00O00O0 :return _O0OO000O0O00O00O0 [OO000OOO00000O0O0 ]#line:25
        return None #line:26
    @staticmethod #line:28
    def wait_until_key (key =None ):#line:29
        if isinstance (key ,str ):#line:30
            OOO00OOO0OOOO0000 =key .lower ()#line:31
            if OOO00OOO0OOOO0000 in _OOO00O0O00O0O0000 :#line:32
                key =_OOO00O0O00O0O0000 [OOO00OOO0OOOO0000 ]#line:33
            elif len (key )==1 :#line:34
                key =ord (key [0 ])#line:35
        while True :#line:36
            if key is None :#line:37
                if cv2 .waitKey (10 )!=-1 :#line:38
                    break #line:39
            elif cv2 .waitKey (10 )==key :#line:40
                break #line:41
    def __init__ (OO0OOO0O0OO0O0OOO ,id =0 ):#line:43
        OO0OOO0O0OO0O0OOO ._title ='window {}'.format (id )#line:44
        Runner .register_component (OO0OOO0O0OO0O0OOO )#line:45
    def dispose (OO0OOOOOO0O000O00 ):#line:47
        cv2 .destroyWindow (OO0OOOOOO0O000O00 ._title )#line:48
        Runner .unregister_component (OO0OOOOOO0O000O00 )#line:49
    def show (O0O00OOO0O0O0OOOO ,OO000O0OO00000OO0 ):#line:51
        if OO000O0OO00000OO0 is not None and OO000O0OO00000OO0 .shape [0 ]>0 and OO000O0OO00000OO0 .shape [1 ]>0 :#line:52
            cv2 .imshow (O0O00OOO0O0O0OOOO ._title ,OO000O0OO00000OO0 )#line:53
    def hide (O0O0O0O0O00O00OO0 ):#line:55
        cv2 .destroyWindow (O0O0O0O0O00O00OO0 ._title )#line:56
