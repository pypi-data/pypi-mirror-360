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

from pynput .keyboard import Listener ,Key #line:2
def _OOO000OO00O000O00 (OO000O000OOOO00OO ):#line:5
    if hasattr (OO000O000OOOO00OO ,'char'):KeyEvent ._pressed_key =OO000O000OOOO00OO .char #line:6
    else :KeyEvent ._pressed_key =OO000O000OOOO00OO #line:7
def _O0OOO0OOOOOO0OO0O (OO000O0O00OOO0000 ):#line:9
    if hasattr (OO000O0O00OOO0000 ,'char'):KeyEvent ._released_key =OO000O0O00OOO0000 .char #line:10
    else :KeyEvent ._released_key =OO000O0O00OOO0000 #line:11
class KeyEvent :#line:14
    SPACE =Key .space #line:15
    ESC =Key .esc #line:16
    _listener =None #line:18
    _pressed_key =None #line:19
    _released_key =None #line:20
    @staticmethod #line:22
    def start ():#line:23
        KeyEvent .stop ()#line:24
        KeyEvent ._listener =Listener (on_press =_OOO000OO00O000O00 ,on_release =_O0OOO0OOOOOO0OO0O )#line:25
        KeyEvent ._listener .start ()#line:26
    @staticmethod #line:28
    def stop ():#line:29
        O0OOO0O000O0000OO =KeyEvent ._listener #line:30
        KeyEvent ._listener =None #line:31
        if O0OOO0O000O0000OO is not None :#line:32
            O0OOO0O000O0000OO .stop ()#line:33
    @staticmethod #line:35
    def get_pressed_key ():#line:36
        OOOO0O00O0OOO000O =KeyEvent ._pressed_key #line:37
        KeyEvent ._pressed_key =None #line:38
        return OOOO0O00O0OOO000O #line:39
    @staticmethod #line:41
    def get_released_key ():#line:42
        OO00O00O00O000O00 =KeyEvent ._released_key #line:43
        KeyEvent ._released_key =None #line:44
        return OO00O00O00O000O00 #line:45
