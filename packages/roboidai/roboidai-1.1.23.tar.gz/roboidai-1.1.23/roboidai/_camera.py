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
_O00O0OO0O000OO0OO ={8 :'bs',9 :'tab',13 :'enter',27 :'esc'}#line:16
_O0OO0OO0OO0O00O00 ={'bs':8 ,'tab':9 ,'enter':13 ,'esc':27 }#line:22
class _OOO0OOOO000O000O0 :#line:25
    _AVOIDS =('192.168.0.1','192.168.1.1')#line:26
    @staticmethod #line:28
    def _connect (OO0OOO0O00O00OO0O ,OOOO000O0OOOOOO00 ):#line:29
        O0O0O0O00O00O0O00 =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:30
        socket .setdefaulttimeout (1 )#line:31
        O000O00OOO0O0000O =O0O0O0O00O00O0O00 .connect_ex ((OO0OOO0O00O00OO0O ,OOOO000O0OOOOOO00 ))#line:32
        O0O0O0O00O00O0O00 .close ()#line:33
        return O000O00OOO0O0000O ==0 #line:34
    @staticmethod #line:36
    def scan (max_ip =5 ,multi =False ,wifi_name =None ,user ='admin',passwd ='admin'):#line:37
        O000000OO00OO0O0O =[]#line:38
        O00000OO0OOOOOO0O =[]#line:39
        O0000OOO00000O0OO =ifaddr .get_adapters ()#line:40
        if wifi_name is None :#line:41
            for O000O0O0OO000OOO0 in O0000OOO00000O0OO [::-1 ]:#line:42
                for O00O00O00O00O000O in O000O0O0OO000OOO0 .ips :#line:43
                    O00O000O0OO0OOOOO =O00O00O00O00O000O .nice_name .lower ()#line:44
                    if 'bluetooth'in O00O000O0OO0OOOOO :continue #line:45
                    if 'loopback'in O00O000O0OO0OOOOO :continue #line:46
                    if O00O00O00O00O000O .ip =='127.0.0.1'or O00O00O00O00O000O .ip =='0.0.0.0':continue #line:47
                    if isinstance (O00O00O00O00O000O .ip ,str ):#line:48
                        OOO0OO000O0O0O000 =O00O00O00O00O000O .ip .split ('.')#line:49
                        if len (OOO0OO000O0O0O000 )>3 and OOO0OO000O0O0O000 [0 ]=='192'and OOO0OO000O0O0O000 [2 ]=='66':#line:50
                            O000000OO00OO0O0O .append (O00O00O00O00O000O .ip )#line:51
        else :#line:52
            for O000O0O0OO000OOO0 in O0000OOO00000O0OO :#line:53
                for O00O00O00O00O000O in O000O0O0OO000OOO0 .ips :#line:54
                    if wifi_name ==O00O00O00O00O000O .nice_name :#line:55
                        if isinstance (O00O00O00O00O000O .ip ,str ):#line:56
                            O000000OO00OO0O0O .append (O00O00O00O00O000O .ip )#line:57
        OO00OOOOOO0O000O0 =('192.168.66.')#line:58
        OO0OOO00000O00OOO =[]#line:59
        O0O0O0O0OO000OOOO =[]#line:60
        for O00O00O00O00O000O in O000000OO00OO0O0O :#line:61
            OOO0OO000O0O0O000 =O00O00O00O00O000O .split ('.')#line:62
            if len (OOO0OO000O0O0O000 )>3 :#line:63
                O0000O0OOOO000OOO ='{}.{}.{}.'.format (OOO0OO000O0O0O000 [0 ],OOO0OO000O0O0O000 [1 ],OOO0OO000O0O0O000 [2 ])#line:64
                if O0000O0OOOO000OOO in OO00OOOOOO0O000O0 :#line:65
                    if O0000O0OOOO000OOO not in OO0OOO00000O00OOO :#line:66
                        OO0OOO00000O00OOO .append (O0000O0OOOO000OOO )#line:67
                else :#line:68
                    if O0000O0OOOO000OOO not in O0O0O0O0OO000OOOO :#line:69
                        O0O0O0O0OO000OOOO .append (O0000O0OOOO000OOO )#line:70
        OO0OOO00000O00OOO .extend (O0O0O0O0OO000OOOO )#line:71
        for OO00O000O00000OOO in range (1 ,max_ip +1 ):#line:73
            OOOO0000OOOOOO000 =[]#line:74
            for O0000O0OOOO000OOO in OO0OOO00000O00OOO :#line:75
                O00OO0O000O00OOOO =O0000O0OOOO000OOO +str (OO00O000O00000OOO )#line:76
                if O00OO0O000O00OOOO not in _OOO0OOOO000O000O0 ._AVOIDS and _OOO0OOOO000O000O0 ._connect (O00OO0O000O00OOOO ,9527 ):#line:77
                    OOO00OOOO0O0OOO00 =cv2 .VideoCapture ('http://'+O00OO0O000O00OOOO +':9527/videostream.cgi?loginuse='+user +'&loginpas='+passwd )#line:78
                    if OOO00OOOO0O0OOO00 .isOpened ():#line:79
                        O00000OO0OOOOOO0O .append (OOO00OOOO0O0OOO00 )#line:80
                        if multi :#line:81
                            OOOO0000OOOOOO000 .append (O0000O0OOOO000OOO )#line:82
                        else :#line:83
                            return O00000OO0OOOOOO0O #line:84
            if OOOO0000OOOOOO000 :#line:85
                OO0OOO00000O00OOO =[O0O000OO0OOO0OOO0 for O0O000OO0OOO0OOO0 in OO0OOO00000O00OOO if O0O000OO0OOO0OOO0 not in OOOO0000OOOOOO000 ]#line:86
                OOOO0000OOOOOO000 =[]#line:87
        return O00000OO0OOOOOO0O #line:88
class Camera :#line:91
    @staticmethod #line:92
    def test (target ='all',max_usb =10 ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:93
        OOO0OOOOO00OOO0O0 ={}#line:94
        OO0O0O00O0O0O0O00 ={}#line:95
        if isinstance (target ,str ):#line:96
            target =target .lower ()#line:97
        if target =='all'or target =='usb':#line:98
            print ('scanning usb camera...')#line:99
            for OO00OOO0OOOOO0000 in range (max_usb +1 ):#line:100
                O0O000OOOO0O0000O =cv2 .VideoCapture (OO00OOO0OOOOO0000 )#line:101
                if O0O000OOOO0O0000O .isOpened ():#line:102
                    OOO0OOOOO00OOO0O0 [OO00OOO0OOOOO0000 ]=O0O000OOOO0O0000O #line:103
        if target =='all'or target =='ip':#line:104
            print ('scanning ip camera...')#line:105
            for OO00OOO0OOOOO0000 ,O0O000OOOO0O0000O in enumerate (_OOO0OOOO000O000O0 .scan (max_ip ,False ,wifi_name ,user ,passwd )):#line:106
                OO0O0O00O0O0O0O00 [OO00OOO0OOOOO0000 ]=O0O000OOOO0O0000O #line:107
        print ('scanning completed')#line:108
        while True :#line:109
            for OO00OOO0OOOOO0000 in OOO0OOOOO00OOO0O0 :#line:110
                O0000OO0O000OOOO0 ,OO000O0O000O0O0OO =OOO0OOOOO00OOO0O0 [OO00OOO0OOOOO0000 ].read ()#line:111
                if O0000OO0O000OOOO0 :#line:112
                    cv2 .putText (OO000O0O000O0O0OO ,'press ESC key to quit',(30 ,40 ),cv2 .FONT_HERSHEY_SIMPLEX ,1 ,(255 ,255 ,255 ),2 )#line:113
                    cv2 .imshow ('camera usb{}'.format (OO00OOO0OOOOO0000 ),OO000O0O000O0O0OO )#line:114
            for OO00OOO0OOOOO0000 in OO0O0O00O0O0O0O00 :#line:115
                O0000OO0O000OOOO0 ,OO000O0O000O0O0OO =OO0O0O00O0O0O0O00 [OO00OOO0OOOOO0000 ].read ()#line:116
                if O0000OO0O000OOOO0 :#line:117
                    OO000O0O000O0O0OO =OO000O0O000O0O0OO [40 :,:]#line:118
                    cv2 .putText (OO000O0O000O0O0OO ,'press ESC key to quit',(30 ,40 ),cv2 .FONT_HERSHEY_SIMPLEX ,1 ,(255 ,255 ,255 ),2 )#line:119
                    cv2 .imshow ('camera ip{}'.format (OO00OOO0OOOOO0000 ),OO000O0O000O0O0OO )#line:120
            if cv2 .waitKey (1 )==27 :#line:121
                break #line:122
        for OO00OOO0OOOOO0000 in OOO0OOOOO00OOO0O0 :#line:123
            OOO0OOOOO00OOO0O0 [OO00OOO0OOOOO0000 ].release ()#line:124
        for OO00OOO0OOOOO0000 in OO0O0O00O0O0O0O00 :#line:125
            OO0O0O00O0O0O0O00 [OO00OOO0OOOOO0000 ].release ()#line:126
        cv2 .destroyAllWindows ()#line:127
    @staticmethod #line:129
    def check_key (timeout_msec =1 ):#line:130
        O0O0O000000000O0O =cv2 .waitKey (timeout_msec )#line:131
        if O0O0O000000000O0O >=32 and O0O0O000000000O0O <=126 :return chr (O0O0O000000000O0O )#line:132
        elif O0O0O000000000O0O in _O00O0OO0O000OO0OO :return _O00O0OO0O000OO0OO [O0O0O000000000O0O ]#line:133
        return None #line:134
    @staticmethod #line:136
    def wait_until_key (key =None ):#line:137
        if isinstance (key ,str ):#line:138
            O0OOO00OO0OOOOO00 =key .lower ()#line:139
            if O0OOO00OO0OOOOO00 in _O0OO0OO0OO0O00O00 :#line:140
                key =_O0OO0OO0OO0O00O00 [O0OOO00OO0OOOOO00 ]#line:141
            elif len (key )==1 :#line:142
                key =ord (key [0 ])#line:143
        while True :#line:144
            if key is None :#line:145
                if cv2 .waitKey (10 )!=-1 :#line:146
                    break #line:147
            elif cv2 .waitKey (10 )==key :#line:148
                break #line:149
    def __init__ (O0O0OO000OO0OO000 ,id =0 ,flip =None ,square =False ,crop =True ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:151
        O00OO0O00O0OOOO0O =None #line:152
        OOOOOOOOO00O0O000 =''#line:153
        try :#line:154
            if isinstance (id ,(int ,float )):#line:155
                id =int (id )#line:156
                OOOOOOOOO00O0O000 ='usb{}'.format (id )#line:157
                O00OO0O00O0OOOO0O =O0O0OO000OO0OO000 ._create_usb_cam (id ,OOOOOOOOO00O0O000 )#line:158
            elif isinstance (id ,str ):#line:159
                id =id .lower ()#line:160
                OOOOOOOOO00O0O000 =id #line:161
                if id .startswith ('usb'):#line:162
                    O00OO0O00O0OOOO0O =O0O0OO000OO0OO000 ._create_usb_cam (int (id [3 :]),OOOOOOOOO00O0O000 )#line:163
                elif id .startswith ('ip'):#line:164
                    O00OO0O00O0OOOO0O =O0O0OO000OO0OO000 ._create_ip_cam (int (id [2 :]),OOOOOOOOO00O0O000 ,max_ip ,wifi_name ,user ,passwd )#line:165
        except :#line:166
            print ('Cannot open camera',OOOOOOOOO00O0O000 )#line:167
        O0O0OO000OO0OO000 .set_flip (flip )#line:168
        O0O0OO000OO0OO000 .set_square (square )#line:169
        O0O0OO000OO0OO000 ._crop =crop #line:170
        O0O0OO000OO0OO000 ._cap =O00OO0O00O0OOOO0O #line:171
        O0O0OO000OO0OO000 ._title =OOOOOOOOO00O0O000 #line:172
        O0O0OO000OO0OO000 ._frame =None #line:173
        O0O0OO000OO0OO000 ._width =0 #line:174
        O0O0OO000OO0OO000 ._height =0 #line:175
        if O00OO0O00O0OOOO0O is not None :#line:176
            Runner .register_component (O0O0OO000OO0OO000 )#line:177
            OO000OO0OO00OO0OO =threading .Thread (target =O0O0OO000OO0OO000 ._run )#line:178
            OO000OO0OO00OO0OO .daemon =True #line:179
            OO000OO0OO00OO0OO .start ()#line:180
    def _run (O0OOO00O000O00O0O ):#line:182
        while True :#line:183
            if O0OOO00O000O00O0O ._cap is not None and O0OOO00O000O00O0O ._cap .isOpened ():#line:184
                OOO0000O000000OO0 ,O00OO0O00OO0O0O0O =O0OOO00O000O00O0O ._cap .read ()#line:185
                if OOO0000O000000OO0 :#line:186
                    O0OOO00O000O00O0O ._frame =O00OO0O00OO0O0O0O #line:187
                    O0OOO00O000O00O0O ._width =O00OO0O00OO0O0O0O .shape [1 ]#line:188
                    O0OOO00O000O00O0O ._height =O00OO0O00OO0O0O0O .shape [0 ]#line:189
                else :#line:190
                    O0OOO00O000O00O0O ._frame =None #line:191
                    O0OOO00O000O00O0O ._width =0 #line:192
                    O0OOO00O000O00O0O ._height =0 #line:193
            time .sleep (.01 )#line:194
    def _create_usb_cam (O000000OOOO000OO0 ,OOOO0O0000OO00O0O ,OO00OO000000O0OOO ):#line:196
        O000000OOOO000OO0 ._ip_cam =False #line:197
        O0O00O00O0O000000 =cv2 .VideoCapture (OOOO0O0000OO00O0O )#line:198
        if O0O00O00O0O000000 .isOpened ():#line:199
            return O0O00O00O0O000000 #line:200
        print ('Cannot open camera',OO00OO000000O0OOO )#line:201
        return None #line:202
    def _create_ip_cam (OO0OO00OOOOO0O000 ,OO0O00O000OO0OO00 ,O0O00OO0O00OOOOOO ,max_ip =5 ,wifi_name =None ,user ='admin',passwd ='admin'):#line:204
        OO0OO00OOOOO0O000 ._ip_cam =True #line:205
        print ('scanning ip camera...')#line:206
        O0000O00O00O0OO00 =_OOO0OOOO000O000O0 .scan (max_ip ,False ,wifi_name ,user ,passwd )#line:207
        print ('scanning completed')#line:208
        if OO0O00O000OO0OO00 >=0 and OO0O00O000OO0OO00 <len (O0000O00O00O0OO00 ):#line:209
            return O0000O00O00O0OO00 [OO0O00O000OO0OO00 ]#line:210
        print ('Cannot open camera',O0O00OO0O00OOOOOO )#line:211
        return None #line:212
    def dispose (O0O0OO000OOO00OO0 ):#line:214
        if O0O0OO000OOO00OO0 ._cap is not None :#line:215
            O0O0OO000OOO00OO0 ._cap .release ()#line:216
        cv2 .destroyWindow (O0O0OO000OOO00OO0 ._title )#line:217
        Runner .unregister_component (O0O0OO000OOO00OO0 )#line:218
    def set_flip (OOOO0OOO00O0OOOO0 ,flip =None ):#line:220
        if flip is None :#line:221
            OOOO0OOO00O0OOOO0 ._flip =None #line:222
        elif isinstance (flip ,str ):#line:223
            flip =flip .lower ()#line:224
            if flip .startswith ('h'):OOOO0OOO00O0OOOO0 ._flip =1 #line:225
            elif flip .startswith ('v'):OOOO0OOO00O0OOOO0 ._flip =0 #line:226
            elif flip .startswith ('a'):OOOO0OOO00O0OOOO0 ._flip =-1 #line:227
            elif flip .startswith ('n'):OOOO0OOO00O0OOOO0 ._flip =None #line:228
    def _to_square (OOOO0OOO0OO0OOOOO ,OOO0O0OO0000OOO00 ):#line:230
        if OOO0O0OO0000OOO00 is not None :#line:231
            O00000000O00000O0 =OOO0O0OO0000OOO00 .shape [1 ]#line:232
            OO0OO00OOOO00O000 =OOO0O0OO0000OOO00 .shape [0 ]#line:233
            if OO0OO00OOOO00O000 >O00000000O00000O0 :#line:234
                OOOO0O0O0OO00OO0O =(OO0OO00OOOO00O000 -O00000000O00000O0 )//2 #line:235
                OOO0O0OO0000OOO00 =OOO0O0OO0000OOO00 [OOOO0O0O0OO00OO0O :OOOO0O0O0OO00OO0O +O00000000O00000O0 ,:]#line:236
            else :#line:237
                OOOO0O0O0OO00OO0O =(O00000000O00000O0 -OO0OO00OOOO00O000 )//2 #line:238
                OOO0O0OO0000OOO00 =OOO0O0OO0000OOO00 [:,OOOO0O0O0OO00OO0O :OOOO0O0O0OO00OO0O +OO0OO00OOOO00O000 ]#line:239
        return OOO0O0OO0000OOO00 #line:240
    def get_width (O000O0O000OO000O0 ):#line:242
        return O000O0O000OO000O0 ._width #line:243
    def get_height (OO0OO0OO0OOO0000O ):#line:245
        return OO0OO0OO0OOO0000O ._height #line:246
    def is_square (O00OOO0O0O00000OO ):#line:248
        return O00OOO0O0O00000OO ._square #line:249
    def set_square (OOO00OOO0O0OO00OO ,OOOO000O0OO0O00O0 ):#line:251
        OOO00OOO0O0OO00OO ._square =OOOO000O0OO0O00O0 #line:252
    def read (O00OO0OOO0OO0OO00 ):#line:254
        OO00O0OO0O0000OOO =O00OO0OOO0OO0OO00 ._frame #line:255
        if OO00O0OO0O0000OOO is not None :#line:256
            if O00OO0OOO0OO0OO00 ._ip_cam and O00OO0OOO0OO0OO00 ._crop :#line:257
                OO00O0OO0O0000OOO =OO00O0OO0O0000OOO [40 :,:]#line:258
            if O00OO0OOO0OO0OO00 ._flip is not None :#line:259
                OO00O0OO0O0000OOO =cv2 .flip (OO00O0OO0O0000OOO ,O00OO0OOO0OO0OO00 ._flip )#line:260
            if O00OO0OOO0OO0OO00 ._square :#line:261
                OO00O0OO0O0000OOO =O00OO0OOO0OO0OO00 ._to_square (OO00O0OO0O0000OOO )#line:262
        return OO00O0OO0O0000OOO #line:263
    def read_until_key (OO0OO00O00O0O000O ):#line:265
        while True :#line:266
            O00O0OO0OOO000OO0 =OO0OO00O00O0O000O .read ()#line:267
            OO0OO00O00O0O000O .show (O00O0OO0OOO000OO0 )#line:268
            OOOO00O0O0OOO0O0O =OO0OO00O00O0O000O .check_key ()#line:270
            if OOOO00O0O0OOO0O0O is not None :#line:271
                return O00O0OO0OOO000OO0 ,OOOO00O0O0OOO0O0O #line:272
    def show (OO0OO00OOO000OO0O ,OOO0O00000000O000 ):#line:274
        if OOO0O00000000O000 is not None and OOO0O00000000O000 .shape [0 ]>0 and OOO0O00000000O000 .shape [1 ]>0 :#line:275
            cv2 .imshow (OO0OO00OOO000OO0O ._title ,OOO0O00000000O000 )#line:276
    def hide (O0OO00OO0OO0OO00O ):#line:278
        cv2 .destroyWindow (O0OO00OO0OO0OO00O ._title )#line:279
    def count_down (OO000OOOOO0000OOO ,count =5 ):#line:281
        OOOO0OOO0O0000O00 =OO000OOOOO0000OOO .read ()#line:282
        if OOOO0OOO0O0000O00 is not None :#line:283
            O00O0000O00O0O000 =OOOO0OOO0O0000O00 .copy ()#line:284
            cv2 .putText (O00O0000O00O0O000 ,str (count ),(0 ,240 ),cv2 .FONT_HERSHEY_SIMPLEX ,10 ,(255 ,255 ,255 ),20 ,16 )#line:285
            OO000OOOOO0000OOO .show (O00O0000O00O0O000 )#line:286
        for OOO00OO0O00000OOO in range (count ,0 ,-1 ):#line:287
            O0OO00OOO0000OO0O =timer ()+1 #line:288
            while timer ()<O0OO00OOO0000OO0O :#line:289
                OOOO0OOO0O0000O00 =OO000OOOOO0000OOO .read ()#line:290
                if OOOO0OOO0O0000O00 is not None :#line:291
                    O00O0000O00O0O000 =OOOO0OOO0O0000O00 .copy ()#line:292
                    cv2 .putText (O00O0000O00O0O000 ,str (OOO00OO0O00000OOO ),(0 ,240 ),cv2 .FONT_HERSHEY_SIMPLEX ,10 ,(255 ,255 ,255 ),20 ,16 )#line:293
                    OO000OOOOO0000OOO .show (O00O0000O00O0O000 )#line:294
                cv2 .waitKey (1 )#line:295
        OOOO0OOO0O0000O00 =OO000OOOOO0000OOO .read ()#line:296
        OO000OOOOO0000OOO .show (OOOO0OOO0O0000O00 )#line:297
        return OOOO0OOO0O0000O00 #line:298
