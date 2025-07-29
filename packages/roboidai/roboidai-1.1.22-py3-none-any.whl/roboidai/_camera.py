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
import ifaddr #line:3
import socket #line:4
import cv2 #line:5
import threading #line:6
import time #line:7
from timeit import default_timer as timer #line:8
_OO0OOOOO0000OO000 ={8 :'bs',9 :'tab',13 :'enter',27 :'esc'}#line:16
_O0000O000O000O0O0 ={'bs':8 ,'tab':9 ,'enter':13 ,'esc':27 }#line:22
class _O0O0OO0O0O0OO0O00 :#line:25
    _AVOIDS =('192.168.0.1','192.168.1.1')#line:26
    @staticmethod #line:28
    def _connect (O0O000OO00OOO00O0 ,O0OOOOOOOOO00000O ):#line:29
        OOO0000OO00OO00OO =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:30
        socket .setdefaulttimeout (1 )#line:31
        O0O0OO000O0O0OOOO =OOO0000OO00OO00OO .connect_ex ((O0O000OO00OOO00O0 ,O0OOOOOOOOO00000O ))#line:32
        OOO0000OO00OO00OO .close ()#line:33
        return O0O0OO000O0O0OOOO ==0 #line:34
    @staticmethod #line:36
    def scan (max_ip =5 ,multi =False ,wifi_name =None ,user ='admin',passwd ='admin'):#line:37
        OO0O00OOOOO0O0OOO =[]#line:38
        O0O00O0OO000OOOOO =[]#line:39
        O00O0O0OOO0O0000O =ifaddr .get_adapters ()#line:40
        if wifi_name is None :#line:41
            for O0OOO0OOOOOOO0OO0 in O00O0O0OOO0O0000O [::-1 ]:#line:42
                for O00OOOO0OO0O0O00O in O0OOO0OOOOOOO0OO0 .ips :#line:43
                    O00OOOOO0O0OOOOO0 =O00OOOO0OO0O0O00O .nice_name .lower ()#line:44
                    if 'bluetooth'in O00OOOOO0O0OOOOO0 :continue #line:45
                    if 'loopback'in O00OOOOO0O0OOOOO0 :continue #line:46
                    if O00OOOO0OO0O0O00O .ip =='127.0.0.1'or O00OOOO0OO0O0O00O .ip =='0.0.0.0':continue #line:47
                    if isinstance (O00OOOO0OO0O0O00O .ip ,str ):#line:48
                        O0O0O0OO0O0O0OO00 =O00OOOO0OO0O0O00O .ip .split ('.')#line:49
                        if len (O0O0O0OO0O0O0OO00 )>3 and O0O0O0OO0O0O0OO00 [0 ]=='192'and O0O0O0OO0O0O0OO00 [2 ]=='66':#line:50
                            OO0O00OOOOO0O0OOO .append (O00OOOO0OO0O0O00O .ip )#line:51
        else :#line:52
            for O0OOO0OOOOOOO0OO0 in O00O0O0OOO0O0000O :#line:53
                for O00OOOO0OO0O0O00O in O0OOO0OOOOOOO0OO0 .ips :#line:54
                    if wifi_name ==O00OOOO0OO0O0O00O .nice_name :#line:55
                        if isinstance (O00OOOO0OO0O0O00O .ip ,str ):#line:56
                            OO0O00OOOOO0O0OOO .append (O00OOOO0OO0O0O00O .ip )#line:57
        OO0000000O00O0O0O =('192.168.66.')#line:58
        O0000000OO0OOO00O =[]#line:59
        O0000O000OOO0OO0O =[]#line:60
        for O00OOOO0OO0O0O00O in OO0O00OOOOO0O0OOO :#line:61
            O0O0O0OO0O0O0OO00 =O00OOOO0OO0O0O00O .split ('.')#line:62
            if len (O0O0O0OO0O0O0OO00 )>3 :#line:63
                OO00OOOOO0O000OO0 ='{}.{}.{}.'.format (O0O0O0OO0O0O0OO00 [0 ],O0O0O0OO0O0O0OO00 [1 ],O0O0O0OO0O0O0OO00 [2 ])#line:64
                if OO00OOOOO0O000OO0 in OO0000000O00O0O0O :#line:65
                    if OO00OOOOO0O000OO0 not in O0000000OO0OOO00O :#line:66
                        O0000000OO0OOO00O .append (OO00OOOOO0O000OO0 )#line:67
                else :#line:68
                    if OO00OOOOO0O000OO0 not in O0000O000OOO0OO0O :#line:69
                        O0000O000OOO0OO0O .append (OO00OOOOO0O000OO0 )#line:70
        O0000000OO0OOO00O .extend (O0000O000OOO0OO0O )#line:71
        for O0O00000O00O0O0OO in range (1 ,max_ip +1 ):#line:73
            O0OO00O0OOO000O00 =[]#line:74
            for OO00OOOOO0O000OO0 in O0000000OO0OOO00O :#line:75
                OOO0OOOO0OO0OOO00 =OO00OOOOO0O000OO0 +str (O0O00000O00O0O0OO )#line:76
                if OOO0OOOO0OO0OOO00 not in _O0O0OO0O0O0OO0O00 ._AVOIDS and _O0O0OO0O0O0OO0O00 ._connect (OOO0OOOO0OO0OOO00 ,9527 ):#line:77
                    O000OOOOO00000000 =cv2 .VideoCapture ('http://'+OOO0OOOO0OO0OOO00 +':9527/videostream.cgi?loginuse='+user +'&loginpas='+passwd )#line:78
                    if O000OOOOO00000000 .isOpened ():#line:79
                        O0O00O0OO000OOOOO .append (O000OOOOO00000000 )#line:80
                        if multi :#line:81
                            O0OO00O0OOO000O00 .append (OO00OOOOO0O000OO0 )#line:82
                        else :#line:83
                            return O0O00O0OO000OOOOO #line:84
            if O0OO00O0OOO000O00 :#line:85
                O0000000OO0OOO00O =[O0O0O00000OO000OO for O0O0O00000OO000OO in O0000000OO0OOO00O if O0O0O00000OO000OO not in O0OO00O0OOO000O00 ]#line:86
                O0OO00O0OOO000O00 =[]#line:87
        return O0O00O0OO000OOOOO #line:88
class Camera :#line:91
    @staticmethod #line:92
    def test (target ='all',max_usb =10 ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:93
        O0O00O00O0000O00O ={}#line:94
        OOO0OOOO000O00O00 ={}#line:95
        if isinstance (target ,str ):#line:96
            target =target .lower ()#line:97
        if target =='all'or target =='usb':#line:98
            print ('scanning usb camera...')#line:99
            for O000000O00O000O00 in range (max_usb +1 ):#line:100
                O00OOO00O000O0000 =cv2 .VideoCapture (O000000O00O000O00 )#line:101
                if O00OOO00O000O0000 .isOpened ():#line:102
                    O0O00O00O0000O00O [O000000O00O000O00 ]=O00OOO00O000O0000 #line:103
        if target =='all'or target =='ip':#line:104
            print ('scanning ip camera...')#line:105
            for O000000O00O000O00 ,O00OOO00O000O0000 in enumerate (_O0O0OO0O0O0OO0O00 .scan (max_ip ,False ,wifi_name ,user ,passwd )):#line:106
                OOO0OOOO000O00O00 [O000000O00O000O00 ]=O00OOO00O000O0000 #line:107
        print ('scanning completed')#line:108
        while True :#line:109
            for O000000O00O000O00 in O0O00O00O0000O00O :#line:110
                O000O0000OOO00O0O ,O0O000OO000OOOOOO =O0O00O00O0000O00O [O000000O00O000O00 ].read ()#line:111
                if O000O0000OOO00O0O :#line:112
                    cv2 .putText (O0O000OO000OOOOOO ,'press ESC key to quit',(30 ,40 ),cv2 .FONT_HERSHEY_SIMPLEX ,1 ,(255 ,255 ,255 ),2 )#line:113
                    cv2 .imshow ('camera usb{}'.format (O000000O00O000O00 ),O0O000OO000OOOOOO )#line:114
            for O000000O00O000O00 in OOO0OOOO000O00O00 :#line:115
                O000O0000OOO00O0O ,O0O000OO000OOOOOO =OOO0OOOO000O00O00 [O000000O00O000O00 ].read ()#line:116
                if O000O0000OOO00O0O :#line:117
                    O0O000OO000OOOOOO =O0O000OO000OOOOOO [40 :,:]#line:118
                    cv2 .putText (O0O000OO000OOOOOO ,'press ESC key to quit',(30 ,40 ),cv2 .FONT_HERSHEY_SIMPLEX ,1 ,(255 ,255 ,255 ),2 )#line:119
                    cv2 .imshow ('camera ip{}'.format (O000000O00O000O00 ),O0O000OO000OOOOOO )#line:120
            if cv2 .waitKey (1 )==27 :#line:121
                break #line:122
        for O000000O00O000O00 in O0O00O00O0000O00O :#line:123
            O0O00O00O0000O00O [O000000O00O000O00 ].release ()#line:124
        for O000000O00O000O00 in OOO0OOOO000O00O00 :#line:125
            OOO0OOOO000O00O00 [O000000O00O000O00 ].release ()#line:126
        cv2 .destroyAllWindows ()#line:127
    @staticmethod #line:129
    def check_key (timeout_msec =1 ):#line:130
        OOOO0O0000O0O00OO =cv2 .waitKey (timeout_msec )#line:131
        if OOOO0O0000O0O00OO >=32 and OOOO0O0000O0O00OO <=126 :return chr (OOOO0O0000O0O00OO )#line:132
        elif OOOO0O0000O0O00OO in _OO0OOOOO0000OO000 :return _OO0OOOOO0000OO000 [OOOO0O0000O0O00OO ]#line:133
        return None #line:134
    @staticmethod #line:136
    def wait_until_key (key =None ):#line:137
        if isinstance (key ,str ):#line:138
            O0O0OOO000O000000 =key .lower ()#line:139
            if O0O0OOO000O000000 in _O0000O000O000O0O0 :#line:140
                key =_O0000O000O000O0O0 [O0O0OOO000O000000 ]#line:141
            elif len (key )==1 :#line:142
                key =ord (key [0 ])#line:143
        while True :#line:144
            if key is None :#line:145
                if cv2 .waitKey (10 )!=-1 :#line:146
                    break #line:147
            elif cv2 .waitKey (10 )==key :#line:148
                break #line:149
    def __init__ (OO0000OOO0000OOO0 ,id =0 ,flip =None ,square =False ,crop =True ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:151
        OOOOOOO0000OOOOO0 =None #line:152
        OOO000O000O00OOOO =''#line:153
        try :#line:154
            if isinstance (id ,(int ,float )):#line:155
                id =int (id )#line:156
                OOO000O000O00OOOO ='usb{}'.format (id )#line:157
                OOOOOOO0000OOOOO0 =OO0000OOO0000OOO0 ._create_usb_cam (id ,OOO000O000O00OOOO )#line:158
            elif isinstance (id ,str ):#line:159
                id =id .lower ()#line:160
                OOO000O000O00OOOO =id #line:161
                if id .startswith ('usb'):#line:162
                    OOOOOOO0000OOOOO0 =OO0000OOO0000OOO0 ._create_usb_cam (int (id [3 :]),OOO000O000O00OOOO )#line:163
                elif id .startswith ('ip'):#line:164
                    OOOOOOO0000OOOOO0 =OO0000OOO0000OOO0 ._create_ip_cam (int (id [2 :]),OOO000O000O00OOOO ,max_ip ,wifi_name ,user ,passwd )#line:165
        except :#line:166
            print ('Cannot open camera',OOO000O000O00OOOO )#line:167
        OO0000OOO0000OOO0 .set_flip (flip )#line:168
        OO0000OOO0000OOO0 .set_square (square )#line:169
        OO0000OOO0000OOO0 ._crop =crop #line:170
        OO0000OOO0000OOO0 ._cap =OOOOOOO0000OOOOO0 #line:171
        OO0000OOO0000OOO0 ._title =OOO000O000O00OOOO #line:172
        OO0000OOO0000OOO0 ._frame =None #line:173
        OO0000OOO0000OOO0 ._width =0 #line:174
        OO0000OOO0000OOO0 ._height =0 #line:175
        if OOOOOOO0000OOOOO0 is not None :#line:176
            Runner .register_component (OO0000OOO0000OOO0 )#line:177
            OOO0OOO0OO0O00000 =threading .Thread (target =OO0000OOO0000OOO0 ._run )#line:178
            OOO0OOO0OO0O00000 .daemon =True #line:179
            OOO0OOO0OO0O00000 .start ()#line:180
    def _run (O000O0OOOO0O0O0O0 ):#line:182
        while True :#line:183
            if O000O0OOOO0O0O0O0 ._cap is not None and O000O0OOOO0O0O0O0 ._cap .isOpened ():#line:184
                O0OOOO00000O0OOOO ,OOO00O0OO0O000OO0 =O000O0OOOO0O0O0O0 ._cap .read ()#line:185
                if O0OOOO00000O0OOOO :#line:186
                    O000O0OOOO0O0O0O0 ._frame =OOO00O0OO0O000OO0 #line:187
                    O000O0OOOO0O0O0O0 ._width =OOO00O0OO0O000OO0 .shape [1 ]#line:188
                    O000O0OOOO0O0O0O0 ._height =OOO00O0OO0O000OO0 .shape [0 ]#line:189
                else :#line:190
                    O000O0OOOO0O0O0O0 ._frame =None #line:191
                    O000O0OOOO0O0O0O0 ._width =0 #line:192
                    O000O0OOOO0O0O0O0 ._height =0 #line:193
            time .sleep (.01 )#line:194
    def _create_usb_cam (O0O00OO0OOOOOO0OO ,OOOOO00OO00OOOOOO ,O00OO0000O00OO0OO ):#line:196
        O0O00OO0OOOOOO0OO ._ip_cam =False #line:197
        O00O0O0O00OOO000O =cv2 .VideoCapture (OOOOO00OO00OOOOOO )#line:198
        if O00O0O0O00OOO000O .isOpened ():#line:199
            return O00O0O0O00OOO000O #line:200
        print ('Cannot open camera',O00OO0000O00OO0OO )#line:201
        return None #line:202
    def _create_ip_cam (O0O00O00O00000O0O ,O0OOOO0000O0O0OOO ,OOOOO0OOO0OO0O0O0 ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:204
        O0O00O00O00000O0O ._ip_cam =True #line:205
        print ('scanning ip camera...')#line:206
        OOOOOO0OOO0O0OO0O =_O0O0OO0O0O0OO0O00 .scan (max_ip ,False ,wifi_name ,user ,passwd )#line:207
        print ('scanning completed')#line:208
        if O0OOOO0000O0O0OOO >=0 and O0OOOO0000O0O0OOO <len (OOOOOO0OOO0O0OO0O ):#line:209
            return OOOOOO0OOO0O0OO0O [O0OOOO0000O0O0OOO ]#line:210
        print ('Cannot open camera',OOOOO0OOO0OO0O0O0 )#line:211
        return None #line:212
    def dispose (O00O0OO0000000O0O ):#line:214
        if O00O0OO0000000O0O ._cap is not None :#line:215
            O00O0OO0000000O0O ._cap .release ()#line:216
        cv2 .destroyWindow (O00O0OO0000000O0O ._title )#line:217
        Runner .unregister_component (O00O0OO0000000O0O )#line:218
    def set_flip (O00O0O000OOOOOO00 ,flip =None ):#line:220
        if flip is None :#line:221
            O00O0O000OOOOOO00 ._flip =None #line:222
        elif isinstance (flip ,str ):#line:223
            flip =flip .lower ()#line:224
            if flip .startswith ('h'):O00O0O000OOOOOO00 ._flip =1 #line:225
            elif flip .startswith ('v'):O00O0O000OOOOOO00 ._flip =0 #line:226
            elif flip .startswith ('a'):O00O0O000OOOOOO00 ._flip =-1 #line:227
            elif flip .startswith ('n'):O00O0O000OOOOOO00 ._flip =None #line:228
    def _to_square (O00OOOO0OOO0O0OOO ,O000O000O00O0OOO0 ):#line:230
        if O000O000O00O0OOO0 is not None :#line:231
            O0000OOO0O0O0O0O0 =O000O000O00O0OOO0 .shape [1 ]#line:232
            O0OOOO000O00OOOO0 =O000O000O00O0OOO0 .shape [0 ]#line:233
            if O0OOOO000O00OOOO0 >O0000OOO0O0O0O0O0 :#line:234
                OOOO0O000000OOOOO =(O0OOOO000O00OOOO0 -O0000OOO0O0O0O0O0 )//2 #line:235
                O000O000O00O0OOO0 =O000O000O00O0OOO0 [OOOO0O000000OOOOO :OOOO0O000000OOOOO +O0000OOO0O0O0O0O0 ,:]#line:236
            else :#line:237
                OOOO0O000000OOOOO =(O0000OOO0O0O0O0O0 -O0OOOO000O00OOOO0 )//2 #line:238
                O000O000O00O0OOO0 =O000O000O00O0OOO0 [:,OOOO0O000000OOOOO :OOOO0O000000OOOOO +O0OOOO000O00OOOO0 ]#line:239
        return O000O000O00O0OOO0 #line:240
    def get_width (O000000O00O00OO00 ):#line:242
        return O000000O00O00OO00 ._width #line:243
    def get_height (O0O000OO0O00OOO0O ):#line:245
        return O0O000OO0O00OOO0O ._height #line:246
    def is_square (O0OOO0OOOOOOOOO00 ):#line:248
        return O0OOO0OOOOOOOOO00 ._square #line:249
    def set_square (O0000O000OO0OOO00 ,O0O000OOOOO0000OO ):#line:251
        O0000O000OO0OOO00 ._square =O0O000OOOOO0000OO #line:252
    def read (O0O00O0OO0OO0000O ):#line:254
        O00000O000O0O0OO0 =O0O00O0OO0OO0000O ._frame #line:255
        if O00000O000O0O0OO0 is not None :#line:256
            if O0O00O0OO0OO0000O ._ip_cam and O0O00O0OO0OO0000O ._crop :#line:257
                O00000O000O0O0OO0 =O00000O000O0O0OO0 [40 :,:]#line:258
            if O0O00O0OO0OO0000O ._flip is not None :#line:259
                O00000O000O0O0OO0 =cv2 .flip (O00000O000O0O0OO0 ,O0O00O0OO0OO0000O ._flip )#line:260
            if O0O00O0OO0OO0000O ._square :#line:261
                O00000O000O0O0OO0 =O0O00O0OO0OO0000O ._to_square (O00000O000O0O0OO0 )#line:262
        return O00000O000O0O0OO0 #line:263
    def read_until_key (O00O0OO00000OO0OO ):#line:265
        while True :#line:266
            OO000000O0OO00OO0 =O00O0OO00000OO0OO .read ()#line:267
            O00O0OO00000OO0OO .show (OO000000O0OO00OO0 )#line:268
            OO0O000OO0O00O00O =O00O0OO00000OO0OO .check_key ()#line:270
            if OO0O000OO0O00O00O is not None :#line:271
                return OO000000O0OO00OO0 ,OO0O000OO0O00O00O #line:272
    def show (O00OOOOOO0O000000 ,OO00O0OOO0O0O0000 ):#line:274
        if OO00O0OOO0O0O0000 is not None and OO00O0OOO0O0O0000 .shape [0 ]>0 and OO00O0OOO0O0O0000 .shape [1 ]>0 :#line:275
            cv2 .imshow (O00OOOOOO0O000000 ._title ,OO00O0OOO0O0O0000 )#line:276
    def hide (O000O0OOO00OO000O ):#line:278
        cv2 .destroyWindow (O000O0OOO00OO000O ._title )#line:279
    def count_down (O0O0OOO00OOO0OOOO ,count =5 ):#line:281
        O0OOO000O0OO000OO =O0O0OOO00OOO0OOOO .read ()#line:282
        if O0OOO000O0OO000OO is not None :#line:283
            O0O00OO0OOOO00000 =O0OOO000O0OO000OO .copy ()#line:284
            cv2 .putText (O0O00OO0OOOO00000 ,str (count ),(0 ,240 ),cv2 .FONT_HERSHEY_SIMPLEX ,10 ,(255 ,255 ,255 ),20 ,16 )#line:285
            O0O0OOO00OOO0OOOO .show (O0O00OO0OOOO00000 )#line:286
        for O00O00O00O0OOO0O0 in range (count ,0 ,-1 ):#line:287
            O0OO0O0O000OOO0O0 =timer ()+1 #line:288
            while timer ()<O0OO0O0O000OOO0O0 :#line:289
                O0OOO000O0OO000OO =O0O0OOO00OOO0OOOO .read ()#line:290
                if O0OOO000O0OO000OO is not None :#line:291
                    O0O00OO0OOOO00000 =O0OOO000O0OO000OO .copy ()#line:292
                    cv2 .putText (O0O00OO0OOOO00000 ,str (O00O00O00O0OOO0O0 ),(0 ,240 ),cv2 .FONT_HERSHEY_SIMPLEX ,10 ,(255 ,255 ,255 ),20 ,16 )#line:293
                    O0O0OOO00OOO0OOOO .show (O0O00OO0OOOO00000 )#line:294
                cv2 .waitKey (1 )#line:295
        O0OOO000O0OO000OO =O0O0OOO00OOO0OOOO .read ()#line:296
        O0O0OOO00OOO0OOOO .show (O0OOO000O0OO000OO )#line:297
        return O0OOO000O0OO000OO #line:298
