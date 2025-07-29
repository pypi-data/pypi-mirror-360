import cv2 #line:1
import os #line:2
import numpy as np #line:3
from ._tool import DownloadTool #line:4
class FaceMarkerDetector :#line:7
    _DEFAULT_FOLDER ='c:/roboid/model'#line:8
    def __init__ (O00O000O0O0O000O0 ):#line:10
        from ._face_detector import FaceDetector #line:11
        O00O000O0O0O000O0 ._loaded =False #line:12
        O00O000O0O0O000O0 ._face_detector =FaceDetector ()#line:13
        O00O000O0O0O000O0 ._facemark =cv2 .face .createFacemarkLBF ()#line:14
        O00O000O0O0O000O0 ._clear ()#line:15
    def _clear (O00O0OO0O0OOO00O0 ):#line:17
        O00O0OO0O0OOO00O0 ._landmarks =np .array ([])#line:18
    def load_model (O0O0OOOOO000OO0O0 ,folder =None ):#line:20
        try :#line:21
            if folder is None :#line:22
                folder =FaceMarkerDetector ._DEFAULT_FOLDER #line:23
            OO0OO0OOOOO0OO0OO =os .path .join (folder ,'face_marker.yaml')#line:24
            if os .path .exists (OO0OO0OOOOO0OO0OO ):#line:25
                O0O0OOOOO000OO0O0 ._facemark .loadModel (OO0OO0OOOOO0OO0OO )#line:26
                O0O0OOOOO000OO0O0 ._loaded =True #line:27
                return True #line:28
            elif isinstance (folder ,str ):#line:29
                if not folder .endswith ('.yaml'):#line:30
                    folder +='.yaml'#line:31
                O0O0OOOOO000OO0O0 ._facemark .loadModel (folder )#line:32
                O0O0OOOOO000OO0O0 ._loaded =True #line:33
                return True #line:34
            else :#line:35
                return False #line:36
        except :#line:37
            return False #line:38
    def download_model (OOOOOOOO00O0000O0 ,folder =None ,overwrite =False ):#line:40
        print ('model downloading...')#line:41
        if folder is None :#line:42
            folder =FaceMarkerDetector ._DEFAULT_FOLDER #line:43
        if not os .path .isdir (folder ):#line:44
            os .makedirs (folder )#line:45
        DownloadTool .download_model (folder ,'face_marker.yaml',overwrite )#line:46
    def detect (O0OO0O000O000OO0O ,O0O0O0OO0O0O00O00 ,gpu =False ):#line:48
        if O0O0O0OO0O0O00O00 is None :#line:49
            O0OO0O000O000OO0O ._clear ()#line:50
        elif O0OO0O000O000OO0O ._loaded :#line:51
            if O0OO0O000O000OO0O ._face_detector .detect (O0O0O0OO0O0O00O00 ,padding =20 ,gpu =gpu ):#line:52
                O0OO00O0OO000O0OO =O0OO0O000O000OO0O ._face_detector .get_box ()#line:53
                if O0OO00O0OO000O0OO is None :#line:54
                    O0OO0O000O000OO0O ._clear ()#line:55
                else :#line:56
                    _OO0O0OOOOOOOO0O00 =np .array ([[O0OO00O0OO000O0OO [0 ],O0OO00O0OO000O0OO [1 ],O0OO00O0OO000O0OO [2 ]-O0OO00O0OO000O0OO [0 ],O0OO00O0OO000O0OO [3 ]-O0OO00O0OO000O0OO [1 ]]])#line:57
                    OO0O00O0O000O0O0O ,OO0OOO000O0O00000 =O0OO0O000O000OO0O ._facemark .fit (O0O0O0OO0O0O00O00 ,_OO0O0OOOOOOOO0O00 )#line:58
                    if OO0O00O0O000O0O0O :#line:59
                        O0OO0O000O000OO0O ._landmarks =OO0OOO000O0O00000 [0 ][0 ]#line:60
                        return True #line:61
                    else :#line:62
                        O0OO0O000O000OO0O ._clear ()#line:63
        return False #line:64
    def _draw_dots (O0O0000O000O000O0 ,O0OOOOO00O0O0OO00 ,color =(255 ,0 ,0 )):#line:66
        OOO0O0O00O000OOOO =np .array ([O0O0000O000O000O0 ._landmarks ])#line:67
        cv2 .face .drawFacemarks (O0OOOOO00O0O0OO00 ,OOO0O0O00O000OOOO ,color )#line:68
    def _draw_polylines (OO00OO0OOO0O00OOO ,O00O0OOO00O000O00 ,OOOOOOOOO0O0O0OO0 ,OOO0000OO0O0O00O0 ,OO0OOOO0O0OOOO000 ,closed =False ,color =(0 ,0 ,255 ),thickness =2 ):#line:70
        OOO00OO0OOOO000O0 =np .array ([OOOOOOOOO0O0O0OO0 [OOOOOOO00O0OO0O0O ]for OOOOOOO00O0OO0O0O in range (OOO0000OO0O0O00O0 ,OO0OOOO0O0OOOO000 +1 )],np .int32 )#line:71
        cv2 .polylines (O00O0OOO00O000O00 ,[OOO00OO0OOOO000O0 ],closed ,color ,thickness )#line:73
    def _draw_lines (O0OO0O00OOO00OO00 ,OOOOOO00O0O00O00O ,color =(0 ,0 ,255 ),thickness =2 ):#line:75
        OOOOOO00O0000OO00 =O0OO0O00OOO00OO00 ._landmarks #line:76
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,0 ,16 )#line:77
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,17 ,21 )#line:78
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,22 ,26 )#line:79
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,27 ,30 )#line:80
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,30 ,35 ,True )#line:81
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,36 ,41 ,True )#line:82
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,42 ,47 ,True )#line:83
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,48 ,59 ,True )#line:84
        O0OO0O00OOO00OO00 ._draw_polylines (OOOOOO00O0O00O00O ,OOOOOO00O0000OO00 ,60 ,67 ,True )#line:85
    def draw_result (O0O000OO0000000O0 ,OOOOO0O00O000O00O ,type ='dot',clone =False ):#line:87
        if OOOOO0O00O000O00O is not None and O0O000OO0000000O0 ._landmarks .size >0 :#line:88
            if clone :#line:89
                OOOOO0O00O000O00O =OOOOO0O00O000O00O .copy ()#line:90
            if type =='dot':#line:91
                O0O000OO0000000O0 ._draw_dots (OOOOO0O00O000O00O )#line:92
            elif type =='line':#line:93
                O0O000OO0000000O0 ._draw_lines (OOOOO0O00O000O00O )#line:94
            else :#line:95
                O0O000OO0000000O0 ._draw_lines (OOOOO0O00O000O00O )#line:96
                O0O000OO0000000O0 ._draw_dots (OOOOO0O00O000O00O )#line:97
        return OOOOO0O00O000O00O #line:98
    def get_marker (O0O00O0O000OOOOOO ,id ='all'):#line:100
        if isinstance (id ,(int ,float )):#line:101
            id =int (id )#line:102
            if id <1 or id >68 :return None #line:103
            return O0O00O0O000OOOOOO ._landmarks [id -1 ]#line:104
        elif isinstance (id ,str ):#line:105
            id =id .lower ()#line:106
            if id =='all':#line:107
                return O0O00O0O000OOOOOO ._landmarks #line:108
            elif id =='left eye':#line:109
                return (O0O00O0O000OOOOOO ._landmarks [36 ]+O0O00O0O000OOOOOO ._landmarks [39 ])/2 #line:110
            elif id =='right eye':#line:111
                return (O0O00O0O000OOOOOO ._landmarks [42 ]+O0O00O0O000OOOOOO ._landmarks [45 ])/2 #line:112
            elif id =='nose':#line:113
                return O0O00O0O000OOOOOO ._landmarks [30 ]#line:114
            elif id =='lip left':#line:115
                return (O0O00O0O000OOOOOO ._landmarks [48 ]+O0O00O0O000OOOOOO ._landmarks [60 ])/2 #line:116
            elif id =='lip right':#line:117
                return (O0O00O0O000OOOOOO ._landmarks [54 ]+O0O00O0O000OOOOOO ._landmarks [64 ])/2 #line:118
            elif id =='lip top':#line:119
                return (O0O00O0O000OOOOOO ._landmarks [51 ]+O0O00O0O000OOOOOO ._landmarks [62 ])/2 #line:120
            elif id =='lip bottom':#line:121
                return (O0O00O0O000OOOOOO ._landmarks [57 ]+O0O00O0O000OOOOOO ._landmarks [66 ])/2 #line:122
            elif id =='lip':#line:123
                return (O0O00O0O000OOOOOO ._landmarks [48 ]+O0O00O0O000OOOOOO ._landmarks [51 ]+O0O00O0O000OOOOOO ._landmarks [54 ]+O0O00O0O000OOOOOO ._landmarks [57 ]+O0O00O0O000OOOOOO ._landmarks [60 ]+O0O00O0O000OOOOOO ._landmarks [62 ]+O0O00O0O000OOOOOO ._landmarks [64 ]+O0O00O0O000OOOOOO ._landmarks [66 ])/8 #line:124
        return O0O00O0O000OOOOOO ._landmarks #line:125
