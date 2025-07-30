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
_O000OOOO00O0000O0 ={8 :'bs',9 :'tab',13 :'enter',27 :'esc'}#line:11
_OOO00O00O0OOO00OO ={'bs':8 ,'tab':9 ,'enter':13 ,'esc':27 }#line:17
class Window :#line:20
    @staticmethod #line:21
    def check_key (timeout_msec =1 ):#line:22
        O00000OO00OO00O0O =cv2 .waitKey (timeout_msec )#line:23
        if O00000OO00OO00O0O >=32 and O00000OO00OO00O0O <=126 :return chr (O00000OO00OO00O0O )#line:24
        elif O00000OO00OO00O0O in _O000OOOO00O0000O0 :return _O000OOOO00O0000O0 [O00000OO00OO00O0O ]#line:25
        return None #line:26
    @staticmethod #line:28
    def wait_until_key (key =None ):#line:29
        if isinstance (key ,str ):#line:30
            OOO0O000OOO000O00 =key .lower ()#line:31
            if OOO0O000OOO000O00 in _OOO00O00O0OOO00OO :#line:32
                key =_OOO00O00O0OOO00OO [OOO0O000OOO000O00 ]#line:33
            elif len (key )==1 :#line:34
                key =ord (key [0 ])#line:35
        while True :#line:36
            if key is None :#line:37
                if cv2 .waitKey (10 )!=-1 :#line:38
                    break #line:39
            elif cv2 .waitKey (10 )==key :#line:40
                break #line:41
    def __init__ (O00OOOO0OOO0OO00O ,id =0 ):#line:43
        O00OOOO0OOO0OO00O ._title ='window {}'.format (id )#line:44
        Runner .register_component (O00OOOO0OOO0OO00O )#line:45
    def dispose (O0O0OOOO0000OOOOO ):#line:47
        cv2 .destroyWindow (O0O0OOOO0000OOOOO ._title )#line:48
        Runner .unregister_component (O0O0OOOO0000OOOOO )#line:49
    def show (OO000OOOOOO0OO0O0 ,OOO0O0OO0O0O00OO0 ):#line:51
        if OOO0O0OO0O0O00OO0 is not None and OOO0O0OO0O0O00OO0 .shape [0 ]>0 and OOO0O0OO0O0O00OO0 .shape [1 ]>0 :#line:52
            cv2 .imshow (OO000OOOOOO0OO0O0 ._title ,OOO0O0OO0O0O00OO0 )#line:53
    def hide (OO00OO0OO00O0OO0O ):#line:55
        cv2 .destroyWindow (OO00OO0OO00O0OO0O ._title )#line:56
