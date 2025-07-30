import cv2 #line:1
import os #line:2
import numpy as np #line:3
from ._tool import DownloadTool #line:4
class FaceMarkerDetector :#line:7
    _DEFAULT_FOLDER ='c:/roboid/model'#line:8
    def __init__ (O00OOOOOOO0000O00 ):#line:10
        from ._face_detector import FaceDetector #line:11
        O00OOOOOOO0000O00 ._loaded =False #line:12
        O00OOOOOOO0000O00 ._face_detector =FaceDetector ()#line:13
        O00OOOOOOO0000O00 ._facemark =cv2 .face .createFacemarkLBF ()#line:14
        O00OOOOOOO0000O00 ._clear ()#line:15
    def _clear (OOOOO00000OOO0OOO ):#line:17
        OOOOO00000OOO0OOO ._landmarks =np .array ([])#line:18
    def load_model (O0OOO0000OO00O00O ,folder =None ):#line:20
        try :#line:21
            if folder is None :#line:22
                folder =FaceMarkerDetector ._DEFAULT_FOLDER #line:23
            O00OO0000OOO00OOO =os .path .join (folder ,'face_marker.yaml')#line:24
            if os .path .exists (O00OO0000OOO00OOO ):#line:25
                O0OOO0000OO00O00O ._facemark .loadModel (O00OO0000OOO00OOO )#line:26
                O0OOO0000OO00O00O ._loaded =True #line:27
                return True #line:28
            elif isinstance (folder ,str ):#line:29
                if not folder .endswith ('.yaml'):#line:30
                    folder +='.yaml'#line:31
                O0OOO0000OO00O00O ._facemark .loadModel (folder )#line:32
                O0OOO0000OO00O00O ._loaded =True #line:33
                return True #line:34
            else :#line:35
                return False #line:36
        except :#line:37
            return False #line:38
    def download_model (OOO0O0O0O0O0OO0O0 ,folder =None ,overwrite =False ):#line:40
        print ('model downloading...')#line:41
        if folder is None :#line:42
            folder =FaceMarkerDetector ._DEFAULT_FOLDER #line:43
        if not os .path .isdir (folder ):#line:44
            os .makedirs (folder )#line:45
        DownloadTool .download_model (folder ,'face_marker.yaml',overwrite )#line:46
    def detect (OOOO000OO0O00000O ,O0OO00OOOOO0O00O0 ,gpu =False ):#line:48
        if O0OO00OOOOO0O00O0 is None :#line:49
            OOOO000OO0O00000O ._clear ()#line:50
        elif OOOO000OO0O00000O ._loaded :#line:51
            if OOOO000OO0O00000O ._face_detector .detect (O0OO00OOOOO0O00O0 ,padding =20 ,gpu =gpu ):#line:52
                O0O0OO0OOO0O00OO0 =OOOO000OO0O00000O ._face_detector .get_box ()#line:53
                if O0O0OO0OOO0O00OO0 is None :#line:54
                    OOOO000OO0O00000O ._clear ()#line:55
                else :#line:56
                    _O0O000OOOO00000OO =np .array ([[O0O0OO0OOO0O00OO0 [0 ],O0O0OO0OOO0O00OO0 [1 ],O0O0OO0OOO0O00OO0 [2 ]-O0O0OO0OOO0O00OO0 [0 ],O0O0OO0OOO0O00OO0 [3 ]-O0O0OO0OOO0O00OO0 [1 ]]])#line:57
                    O0OOOO00O0O00O000 ,OO0O0O0OO0OO0O000 =OOOO000OO0O00000O ._facemark .fit (O0OO00OOOOO0O00O0 ,_O0O000OOOO00000OO )#line:58
                    if O0OOOO00O0O00O000 :#line:59
                        OOOO000OO0O00000O ._landmarks =OO0O0O0OO0OO0O000 [0 ][0 ]#line:60
                        return True #line:61
                    else :#line:62
                        OOOO000OO0O00000O ._clear ()#line:63
        return False #line:64
    def _draw_dots (O000OO00O000O0O00 ,O0O0O0000OO0O0O00 ,color =(255 ,0 ,0 )):#line:66
        O000000O0OOOO00O0 =np .array ([O000OO00O000O0O00 ._landmarks ])#line:67
        cv2 .face .drawFacemarks (O0O0O0000OO0O0O00 ,O000000O0OOOO00O0 ,color )#line:68
    def _draw_polylines (OO00O0OOO0000O000 ,O000O000O00OOOO0O ,O0O0OOOOO0OOO000O ,O00OO00O000OOO00O ,O00O0O0OO00O000OO ,closed =False ,color =(0 ,0 ,255 ),thickness =2 ):#line:70
        O0O0O000O00OOO0OO =np .array ([O0O0OOOOO0OOO000O [OOOO0000OO00O0OOO ]for OOOO0000OO00O0OOO in range (O00OO00O000OOO00O ,O00O0O0OO00O000OO +1 )],np .int32 )#line:71
        cv2 .polylines (O000O000O00OOOO0O ,[O0O0O000O00OOO0OO ],closed ,color ,thickness )#line:73
    def _draw_lines (O0OOO000000O00OOO ,OO0O00000OOOO0OO0 ,color =(0 ,0 ,255 ),thickness =2 ):#line:75
        O000O0O0O000O0OO0 =O0OOO000000O00OOO ._landmarks #line:76
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,0 ,16 )#line:77
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,17 ,21 )#line:78
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,22 ,26 )#line:79
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,27 ,30 )#line:80
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,30 ,35 ,True )#line:81
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,36 ,41 ,True )#line:82
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,42 ,47 ,True )#line:83
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,48 ,59 ,True )#line:84
        O0OOO000000O00OOO ._draw_polylines (OO0O00000OOOO0OO0 ,O000O0O0O000O0OO0 ,60 ,67 ,True )#line:85
    def draw_result (OO000O00OO0OO00O0 ,OOOOO0OOOO0O000O0 ,type ='dot',clone =False ):#line:87
        if OOOOO0OOOO0O000O0 is not None and OO000O00OO0OO00O0 ._landmarks .size >0 :#line:88
            if clone :#line:89
                OOOOO0OOOO0O000O0 =OOOOO0OOOO0O000O0 .copy ()#line:90
            if type =='dot':#line:91
                OO000O00OO0OO00O0 ._draw_dots (OOOOO0OOOO0O000O0 )#line:92
            elif type =='line':#line:93
                OO000O00OO0OO00O0 ._draw_lines (OOOOO0OOOO0O000O0 )#line:94
            else :#line:95
                OO000O00OO0OO00O0 ._draw_lines (OOOOO0OOOO0O000O0 )#line:96
                OO000O00OO0OO00O0 ._draw_dots (OOOOO0OOOO0O000O0 )#line:97
        return OOOOO0OOOO0O000O0 #line:98
    def get_marker (O00OO0OOOO0O00OOO ,id ='all'):#line:100
        if isinstance (id ,(int ,float )):#line:101
            id =int (id )#line:102
            if id <1 or id >68 :return None #line:103
            return O00OO0OOOO0O00OOO ._landmarks [id -1 ]#line:104
        elif isinstance (id ,str ):#line:105
            id =id .lower ()#line:106
            if id =='all':#line:107
                return O00OO0OOOO0O00OOO ._landmarks #line:108
            elif id =='left eye':#line:109
                return (O00OO0OOOO0O00OOO ._landmarks [36 ]+O00OO0OOOO0O00OOO ._landmarks [39 ])/2 #line:110
            elif id =='right eye':#line:111
                return (O00OO0OOOO0O00OOO ._landmarks [42 ]+O00OO0OOOO0O00OOO ._landmarks [45 ])/2 #line:112
            elif id =='nose':#line:113
                return O00OO0OOOO0O00OOO ._landmarks [30 ]#line:114
            elif id =='lip left':#line:115
                return (O00OO0OOOO0O00OOO ._landmarks [48 ]+O00OO0OOOO0O00OOO ._landmarks [60 ])/2 #line:116
            elif id =='lip right':#line:117
                return (O00OO0OOOO0O00OOO ._landmarks [54 ]+O00OO0OOOO0O00OOO ._landmarks [64 ])/2 #line:118
            elif id =='lip top':#line:119
                return (O00OO0OOOO0O00OOO ._landmarks [51 ]+O00OO0OOOO0O00OOO ._landmarks [62 ])/2 #line:120
            elif id =='lip bottom':#line:121
                return (O00OO0OOOO0O00OOO ._landmarks [57 ]+O00OO0OOOO0O00OOO ._landmarks [66 ])/2 #line:122
            elif id =='lip':#line:123
                return (O00OO0OOOO0O00OOO ._landmarks [48 ]+O00OO0OOOO0O00OOO ._landmarks [51 ]+O00OO0OOOO0O00OOO ._landmarks [54 ]+O00OO0OOOO0O00OOO ._landmarks [57 ]+O00OO0OOOO0O00OOO ._landmarks [60 ]+O00OO0OOOO0O00OOO ._landmarks [62 ]+O00OO0OOOO0O00OOO ._landmarks [64 ]+O00OO0OOOO0O00OOO ._landmarks [66 ])/8 #line:124
        return O00OO0OOOO0O00OOO ._landmarks #line:125
