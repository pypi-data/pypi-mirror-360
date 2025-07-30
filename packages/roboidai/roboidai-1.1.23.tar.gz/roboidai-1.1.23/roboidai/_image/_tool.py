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

import cv2 #line:2
import os #line:3
import sys #line:4
from urllib import request #line:5
from datetime import datetime #line:6
class ImageTool :#line:9
    @staticmethod #line:10
    def to_square (O0O000000000O0OOO ,clone =False ):#line:11
        if O0O000000000O0OOO is not None :#line:12
            if clone :#line:13
                O0O000000000O0OOO =O0O000000000O0OOO .copy ()#line:14
            OO0O000OOO00O0000 =O0O000000000O0OOO .shape [1 ]#line:15
            O00O0OOOOO0OO0000 =O0O000000000O0OOO .shape [0 ]#line:16
            if O00O0OOOOO0OO0000 >OO0O000OOO00O0000 :#line:17
                O0O000000O0000O0O =(O00O0OOOOO0OO0000 -OO0O000OOO00O0000 )//2 #line:18
                O0O000000000O0OOO =O0O000000000O0OOO [O0O000000O0000O0O :O0O000000O0000O0O +OO0O000OOO00O0000 ,:]#line:19
            else :#line:20
                O0O000000O0000O0O =(OO0O000OOO00O0000 -O00O0OOOOO0OO0000 )//2 #line:21
                O0O000000000O0OOO =O0O000000000O0OOO [:,O0O000000O0000O0O :O0O000000O0000O0O +O00O0OOOOO0OO0000 ]#line:22
        return O0O000000000O0OOO #line:23
    @staticmethod #line:25
    def resize (O0000000OO0O000OO ,OO00O00OO00OO0O0O ,O0O0O00OO00O00OO0 ):#line:26
        if O0000000OO0O000OO is not None :#line:27
            O0000000OO0O000OO =cv2 .resize (O0000000OO0O000OO ,dsize =(OO00O00OO00OO0O0O ,O0O0O00OO00O00OO0 ))#line:28
        return O0000000OO0O000OO #line:29
    @staticmethod #line:31
    def save (OO00OO00O0OOO0OO0 ,O0O00000O0OO0O00O ,filename =None ):#line:32
        if OO00OO00O0OOO0OO0 is not None and O0O00000O0OO0O00O is not None :#line:33
            if not os .path .isdir (O0O00000O0OO0O00O ):#line:34
                os .makedirs (O0O00000O0OO0O00O )#line:35
            if filename is None :#line:36
                filename =datetime .now ().strftime ("%Y%m%d_%H%M%S_%f")+'.png'#line:37
            if cv2 .imwrite (os .path .join (O0O00000O0OO0O00O ,filename ),OO00OO00O0OOO0OO0 ):#line:38
                return True #line:39
            try :#line:40
                OO000O0OOO0000O0O =os .path .splitext (filename )[1 ]#line:41
                OO0OO00O0OOOO0O00 ,O00O000O00OO00000 =cv2 .imencode (OO000O0OOO0000O0O ,OO00OO00O0OOO0OO0 )#line:42
                if OO0OO00O0OOOO0O00 :#line:43
                    with open (os .path .join (O0O00000O0OO0O00O ,filename ),mode ='w+b')as O00OOOOOOO00O0000 :#line:44
                        O00O000O00OO00000 .tofile (O00OOOOOOO00O0000 )#line:45
                    return True #line:46
                else :#line:47
                    return False #line:48
            except :#line:49
                return False #line:50
        return False #line:51
class DownloadTool :#line:54
    @staticmethod #line:55
    def _print_perc (O0O00OOOO0OO0OO00 ,OO00OO0OO0O0O0000 ,OO000OOO00OOO0000 ):#line:56
        if O0O00OOOO0OO0OO00 >OO00OO0OO0O0O0000 :O0O00OOOO0OO0OO00 =OO00OO0OO0O0O0000 #line:57
        O0O0O0OOOOOO0OO0O =O0O00OOOO0OO0OO00 /OO00OO0OO0O0O0000 #line:58
        O000OOOOOOO0O0OO0 =round (O0O0O0OOOOOO0OO0O *OO000OOO00OOO0000 )#line:59
        if OO00OO0OO0O0O0000 >(1024 **2 ):#line:60
            O0OOO000O0O00OOOO =str (round (OO00OO0OO0O0O0000 /1024 /1024 ,2 ))+'MB'#line:61
        elif OO00OO0OO0O0O0000 >1024 :#line:62
            O0OOO000O0O00OOOO =str (round (OO00OO0OO0O0O0000 /1024 ,2 ))+'KB'#line:63
        else :#line:64
            O0OOO000O0O00OOOO =str (OO00OO0OO0O0O0000 )+'B'#line:65
        print ('\r',DownloadTool ._download_title ,O0OOO000O0O00OOOO ,'#'*O000OOOOOOO0O0OO0 +'-'*(OO000OOO00OOO0000 -O000OOOOOOO0O0OO0 ),'[{:>7.2%}]'.format (O0O0O0OOOOOO0OO0O ),end ='')#line:66
        sys .stdout .flush ()#line:67
    @staticmethod #line:69
    def _download_callback (OO0OO0O0000O0O000 ,OO00OO0OOOO000O00 ,OOO0O0OO000OOOOO0 ):#line:70
        DownloadTool ._print_perc (OO0OO0O0000O0O000 *OO00OO0OOOO000O00 ,OOO0O0OO000OOOOO0 ,20 )#line:71
    @staticmethod #line:73
    def download_model (O0O00OO0000O00000 ,O0OO000OO000O0OOO ,overwrite =False ):#line:74
        OOOOO00O00OO00O00 =os .path .join (O0O00OO0000O00000 ,O0OO000OO000O0OOO )#line:75
        if overwrite or not os .path .exists (OOOOO00O00OO00O00 ):#line:76
            DownloadTool ._download_title =O0OO000OO000O0OOO +':'#line:77
            request .urlretrieve ('http://www.smartrobotmarket.com/hamster/tutorial/class/model/'+O0OO000OO000O0OOO ,OOOOO00O00OO00O00 ,DownloadTool ._download_callback )#line:78
            print ()#line:79
        else :#line:80
            print (O0OO000OO000O0OOO ,'already exists.')#line:81
