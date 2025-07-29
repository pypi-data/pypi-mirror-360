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
    def to_square (O0OOOO00OO00O0OOO ,clone =False ):#line:11
        if O0OOOO00OO00O0OOO is not None :#line:12
            if clone :#line:13
                O0OOOO00OO00O0OOO =O0OOOO00OO00O0OOO .copy ()#line:14
            OOO0OOOO0O000000O =O0OOOO00OO00O0OOO .shape [1 ]#line:15
            OO0OOOOO0OO0O0O0O =O0OOOO00OO00O0OOO .shape [0 ]#line:16
            if OO0OOOOO0OO0O0O0O >OOO0OOOO0O000000O :#line:17
                O000O00OOO0OO0O0O =(OO0OOOOO0OO0O0O0O -OOO0OOOO0O000000O )//2 #line:18
                O0OOOO00OO00O0OOO =O0OOOO00OO00O0OOO [O000O00OOO0OO0O0O :O000O00OOO0OO0O0O +OOO0OOOO0O000000O ,:]#line:19
            else :#line:20
                O000O00OOO0OO0O0O =(OOO0OOOO0O000000O -OO0OOOOO0OO0O0O0O )//2 #line:21
                O0OOOO00OO00O0OOO =O0OOOO00OO00O0OOO [:,O000O00OOO0OO0O0O :O000O00OOO0OO0O0O +OO0OOOOO0OO0O0O0O ]#line:22
        return O0OOOO00OO00O0OOO #line:23
    @staticmethod #line:25
    def resize (O00OOOO0OO0OOO0OO ,OOO0O00OOOO0O000O ,O0OOOO0OO0O00O0OO ):#line:26
        if O00OOOO0OO0OOO0OO is not None :#line:27
            O00OOOO0OO0OOO0OO =cv2 .resize (O00OOOO0OO0OOO0OO ,dsize =(OOO0O00OOOO0O000O ,O0OOOO0OO0O00O0OO ))#line:28
        return O00OOOO0OO0OOO0OO #line:29
    @staticmethod #line:31
    def save (OOO00OOOOO0OOOO0O ,O00OOOOOO0O00000O ,filename =None ):#line:32
        if OOO00OOOOO0OOOO0O is not None and O00OOOOOO0O00000O is not None :#line:33
            if not os .path .isdir (O00OOOOOO0O00000O ):#line:34
                os .makedirs (O00OOOOOO0O00000O )#line:35
            if filename is None :#line:36
                filename =datetime .now ().strftime ("%Y%m%d_%H%M%S_%f")+'.png'#line:37
            if cv2 .imwrite (os .path .join (O00OOOOOO0O00000O ,filename ),OOO00OOOOO0OOOO0O ):#line:38
                return True #line:39
            try :#line:40
                O000O0OOOO00O000O =os .path .splitext (filename )[1 ]#line:41
                OO0O0OO0O0OO00000 ,OO0OOO00OO0O0OO0O =cv2 .imencode (O000O0OOOO00O000O ,OOO00OOOOO0OOOO0O )#line:42
                if OO0O0OO0O0OO00000 :#line:43
                    with open (os .path .join (O00OOOOOO0O00000O ,filename ),mode ='w+b')as OO0OOO0OOOOOOOOO0 :#line:44
                        OO0OOO00OO0O0OO0O .tofile (OO0OOO0OOOOOOOOO0 )#line:45
                    return True #line:46
                else :#line:47
                    return False #line:48
            except :#line:49
                return False #line:50
        return False #line:51
class DownloadTool :#line:54
    @staticmethod #line:55
    def _print_perc (O0O000OO00O0OO000 ,OOOO00O00O000O000 ,OO0O0O0O0O0OOOO0O ):#line:56
        if O0O000OO00O0OO000 >OOOO00O00O000O000 :O0O000OO00O0OO000 =OOOO00O00O000O000 #line:57
        OOOO0OO0O0O0O000O =O0O000OO00O0OO000 /OOOO00O00O000O000 #line:58
        OOO0O00OOOO0000OO =round (OOOO0OO0O0O0O000O *OO0O0O0O0O0OOOO0O )#line:59
        if OOOO00O00O000O000 >(1024 **2 ):#line:60
            OOO000OOO0O0000O0 =str (round (OOOO00O00O000O000 /1024 /1024 ,2 ))+'MB'#line:61
        elif OOOO00O00O000O000 >1024 :#line:62
            OOO000OOO0O0000O0 =str (round (OOOO00O00O000O000 /1024 ,2 ))+'KB'#line:63
        else :#line:64
            OOO000OOO0O0000O0 =str (OOOO00O00O000O000 )+'B'#line:65
        print ('\r',DownloadTool ._download_title ,OOO000OOO0O0000O0 ,'#'*OOO0O00OOOO0000OO +'-'*(OO0O0O0O0O0OOOO0O -OOO0O00OOOO0000OO ),'[{:>7.2%}]'.format (OOOO0OO0O0O0O000O ),end ='')#line:66
        sys .stdout .flush ()#line:67
    @staticmethod #line:69
    def _download_callback (O00000OO0O0O0O0OO ,O00O0OO00O00O0000 ,OO00O0OOO0O000OOO ):#line:70
        DownloadTool ._print_perc (O00000OO0O0O0O0OO *O00O0OO00O00O0000 ,OO00O0OOO0O000OOO ,20 )#line:71
    @staticmethod #line:73
    def download_model (O0OOOOOO0OOOOOOO0 ,OOOO0OOOOO0000O00 ,overwrite =False ):#line:74
        O0OOO000OOOOO0OOO =os .path .join (O0OOOOOO0OOOOOOO0 ,OOOO0OOOOO0000O00 )#line:75
        if overwrite or not os .path .exists (O0OOO000OOOOO0OOO ):#line:76
            DownloadTool ._download_title =OOOO0OOOOO0000O00 +':'#line:77
            request .urlretrieve ('http://www.smartrobotmarket.com/hamster/tutorial/class/model/'+OOOO0OOOOO0000O00 ,O0OOO000OOOOO0OOO ,DownloadTool ._download_callback )#line:78
            print ()#line:79
        else :#line:80
            print (OOOO0OOOOO0000O00 ,'already exists.')#line:81
