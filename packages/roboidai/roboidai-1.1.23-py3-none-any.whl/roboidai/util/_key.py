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

from roboid import wait #line:2
from roboidai ._keyevent import KeyEvent #line:3
from pynput .keyboard import Key #line:4
_O00O00O0O000OO0O0 ={'bs':Key .backspace ,'tab':Key .tab ,'enter':Key .enter ,'esc':Key .esc ,' ':Key .space }#line:13
def wait_until_key (key =None ):#line:16
    if isinstance (key ,str ):#line:17
        O00000O0O0OO0O00O =key .lower ()#line:18
        if O00000O0O0OO0O00O in _O00O00O0O000OO0O0 :#line:19
            key =_O00O00O0O000OO0O0 [O00000O0O0OO0O00O ]#line:20
    KeyEvent .start ()#line:21
    while True :#line:22
        if key is None :#line:23
            if KeyEvent .get_released_key ()is not None :#line:24
                break #line:25
        else :#line:26
            if KeyEvent .get_released_key ()==key :#line:27
                break #line:28
        wait (20 )#line:29
    KeyEvent .stop ()#line:30
