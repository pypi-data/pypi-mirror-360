import cv2 #line:1
import os #line:2
from ._tool import DownloadTool #line:3
class AgeGenderDetector :#line:6
    _AGE_LABELS =['0-2','4-6','8-12','15-20','25-32','38-43','48-53','60-100']#line:7
    _GENDER_LABELS =['male','female']#line:8
    _MODEL_MEAN_VALUES =(78.4263377603 ,87.7689143744 ,114.895847746 )#line:9
    _DEFAULT_FOLDER ='c:/roboid/model'#line:10
    def __init__ (O000OOO0OOOOO000O ):#line:12
        from ._face_detector import FaceDetector #line:13
        O000OOO0OOOOO000O ._age_net =None #line:14
        O000OOO0OOOOO000O ._gender_net =None #line:15
        O000OOO0OOOOO000O ._face_detector =FaceDetector ()#line:16
        O000OOO0OOOOO000O ._clear ()#line:17
    def _clear (OOO0OOOOOO0000OO0 ):#line:19
        OOO0OOOOOO0000OO0 ._age_index =-1 #line:20
        OOO0OOOOOO0000OO0 ._age_label =''#line:21
        OOO0OOOOOO0000OO0 ._age_confidence =0 #line:22
        OOO0OOOOOO0000OO0 ._gender_index =-1 #line:23
        OOO0OOOOOO0000OO0 ._gender_label =''#line:24
        OOO0OOOOOO0000OO0 ._gender_confidence =0 #line:25
    def load_age_model (O0OOO0O0OO0O0000O ,folder =None ):#line:27
        try :#line:28
            if folder is None :#line:29
                folder =AgeGenderDetector ._DEFAULT_FOLDER #line:30
            O0OOO0O0000O0O0O0 =os .path .join (folder ,'age.caffemodel')#line:31
            if os .path .exists (O0OOO0O0000O0O0O0 ):#line:32
                O0OOO0O0OO0O0000O ._age_net =cv2 .dnn .readNet (O0OOO0O0000O0O0O0 ,os .path .join (folder ,'age.prototxt'))#line:33
            else :#line:34
                O0OOO0O0OO0O0000O ._age_net =cv2 .dnn .readNet (folder +'.caffemodel',folder +'.prototxt')#line:35
            return True #line:36
        except :#line:37
            return False #line:38
    def download_age_model (O0O0OOOO0OO00OOO0 ,folder =None ,overwrite =False ):#line:40
        print ('model downloading...')#line:41
        if folder is None :#line:42
            folder =AgeGenderDetector ._DEFAULT_FOLDER #line:43
        if not os .path .isdir (folder ):#line:44
            os .makedirs (folder )#line:45
        DownloadTool .download_model (folder ,'age.caffemodel',overwrite )#line:46
        DownloadTool .download_model (folder ,'age.prototxt',overwrite )#line:47
    def load_gender_model (OOOO00O00000OOOOO ,folder =None ):#line:49
        try :#line:50
            if folder is None :#line:51
                folder =AgeGenderDetector ._DEFAULT_FOLDER #line:52
            OO0O00OOO0OO0O000 =os .path .join (folder ,'gender.caffemodel')#line:53
            if os .path .exists (OO0O00OOO0OO0O000 ):#line:54
                OOOO00O00000OOOOO ._gender_net =cv2 .dnn .readNet (OO0O00OOO0OO0O000 ,os .path .join (folder ,'gender.prototxt'))#line:55
            else :#line:56
                OOOO00O00000OOOOO ._gender_net =cv2 .dnn .readNet (folder +'.caffemodel',folder +'.prototxt')#line:57
            return True #line:58
        except :#line:59
            return False #line:60
    def download_gender_model (O0OOOOO0OOOOO0O0O ,folder =None ,overwrite =False ):#line:62
        print ('model downloading...')#line:63
        if folder is None :#line:64
            folder =AgeGenderDetector ._DEFAULT_FOLDER #line:65
        if not os .path .isdir (folder ):#line:66
            os .makedirs (folder )#line:67
        DownloadTool .download_model (folder ,'gender.caffemodel',overwrite )#line:68
        DownloadTool .download_model (folder ,'gender.prototxt',overwrite )#line:69
    def detect (OOOOO000O0OOOOO0O ,OOO0O0OOOO0OOOO0O ,gpu =False ):#line:71
        if OOO0O0OOOO0OOOO0O is None :#line:72
            OOOOO000O0OOOOO0O ._clear ()#line:73
        elif OOOOO000O0OOOOO0O ._age_net is not None or OOOOO000O0OOOOO0O ._gender_net is not None :#line:74
            if OOOOO000O0OOOOO0O ._face_detector .detect (OOO0O0OOOO0OOOO0O ,padding =20 ):#line:75
                OOOO00O0OOOOOO00O =OOOOO000O0OOOOO0O ._face_detector .crop (OOO0O0OOOO0OOOO0O )#line:76
                if OOOO00O0OOOOOO00O is None :#line:77
                    OOOOO000O0OOOOO0O ._clear ()#line:78
                else :#line:79
                    O0O0O000OOOO0OOO0 =cv2 .dnn .blobFromImage (OOOO00O0OOOOOO00O ,1.0 ,(227 ,227 ),AgeGenderDetector ._MODEL_MEAN_VALUES ,swapRB =False )#line:80
                    if gpu :#line:81
                        OOOOO000O0OOOOO0O ._age_net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:82
                        OOOOO000O0OOOOO0O ._age_net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:83
                    if OOOOO000O0OOOOO0O ._age_net is not None :#line:84
                        OOOOO000O0OOOOO0O ._age_net .setInput (O0O0O000OOOO0OOO0 )#line:85
                        OO00O0O0O0000OOO0 =OOOOO000O0OOOOO0O ._age_net .forward ()[0 ]#line:86
                        O000O0O0000O000O0 =OO00O0O0O0000OOO0 .argmax ()#line:87
                        OOOOO000O0OOOOO0O ._age_index =O000O0O0000O000O0 #line:88
                        OOOOO000O0OOOOO0O ._age_label =AgeGenderDetector ._AGE_LABELS [O000O0O0000O000O0 ]#line:89
                        OOOOO000O0OOOOO0O ._age_confidence =OO00O0O0O0000OOO0 [O000O0O0000O000O0 ]#line:90
                    if OOOOO000O0OOOOO0O ._gender_net is not None :#line:91
                        OOOOO000O0OOOOO0O ._gender_net .setInput (O0O0O000OOOO0OOO0 )#line:92
                        OO00O0O0O0000OOO0 =OOOOO000O0OOOOO0O ._gender_net .forward ()[0 ]#line:93
                        O000O0O0000O000O0 =OO00O0O0O0000OOO0 .argmax ()#line:94
                        OOOOO000O0OOOOO0O ._gender_index =O000O0O0000O000O0 #line:95
                        OOOOO000O0OOOOO0O ._gender_label =AgeGenderDetector ._GENDER_LABELS [O000O0O0000O000O0 ]#line:96
                        OOOOO000O0OOOOO0O ._gender_confidence =OO00O0O0O0000OOO0 [O000O0O0000O000O0 ]#line:97
                    return True #line:98
            else :#line:99
                OOOOO000O0OOOOO0O ._clear ()#line:100
        return False #line:101
    def draw_result (O0O0O00OO00OO0O00 ,O0OOOOO00OOO000O0 ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:103
        if O0OOOOO00OOO000O0 is not None :#line:104
            if clone :#line:105
                O0OOOOO00OOO000O0 =O0OOOOO00OOO000O0 .copy ()#line:106
            O00O0O00OO00O00O0 =O0O0O00OO00OO0O00 ._face_detector .get_box ()#line:107
            if O00O0O00OO00O00O0 is not None :#line:108
                cv2 .rectangle (O0OOOOO00OOO000O0 ,(O00O0O00OO00O00O0 [0 ],O00O0O00OO00O00O0 [1 ]),(O00O0O00OO00O00O0 [2 ],O00O0O00OO00O00O0 [3 ]),color ,thickness )#line:109
                if O0O0O00OO00OO0O00 ._age_net is not None and O0O0O00OO00OO0O00 ._gender_net is not None :#line:110
                    OOOO0O00O0O0OOO00 ='{}, {}'.format (O0O0O00OO00OO0O00 ._age_label ,O0O0O00OO00OO0O00 ._gender_label )#line:111
                elif O0O0O00OO00OO0O00 ._age_net is not None :#line:112
                    OOOO0O00O0O0OOO00 =O0O0O00OO00OO0O00 ._age_label #line:113
                elif O0O0O00OO00OO0O00 ._gender_net is not None :#line:114
                    OOOO0O00O0O0OOO00 =O0O0O00OO00OO0O00 ._gender_label #line:115
                else :#line:116
                    OOOO0O00O0O0OOO00 =''#line:117
                cv2 .putText (O0OOOOO00OOO000O0 ,OOOO0O00O0O0OOO00 ,(O00O0O00OO00O00O0 [0 ],O00O0O00OO00O00O0 [1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,color ,thickness )#line:118
        return O0OOOOO00OOO000O0 #line:119
    def get_age_index (OO0O0OOOOO00O0OO0 ):#line:121
        return OO0O0OOOOO00O0OO0 ._age_index #line:122
    def get_age_label (OOOO00O0OOOO0O0OO ):#line:124
        return OOOO00O0OOOO0O0OO ._age_label #line:125
    def get_age_conf (O00O0OOOOOO0OOO00 ):#line:127
        return O00O0OOOOOO0OOO00 ._age_confidence #line:128
    def get_gender_index (OOOO000OOO0O0O000 ):#line:130
        return OOOO000OOO0O0O000 ._gender_index #line:131
    def get_gender_label (OO0OO0OO00O000O00 ):#line:133
        return OO0OO0OO00O000O00 ._gender_label #line:134
    def get_gender_conf (O000OOOO00O0O0O00 ):#line:136
        return O000OOOO00O0O0O00 ._gender_confidence #line:137
