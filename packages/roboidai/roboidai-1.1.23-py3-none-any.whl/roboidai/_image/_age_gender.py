import cv2 #line:1
import os #line:2
from ._tool import DownloadTool #line:3
class AgeGenderDetector :#line:6
    _AGE_LABELS =['0-2','4-6','8-12','15-20','25-32','38-43','48-53','60-100']#line:7
    _GENDER_LABELS =['male','female']#line:8
    _MODEL_MEAN_VALUES =(78.4263377603 ,87.7689143744 ,114.895847746 )#line:9
    _DEFAULT_FOLDER ='c:/roboid/model'#line:10
    def __init__ (OOO00OO0O0OOOOOO0 ):#line:12
        from ._face_detector import FaceDetector #line:13
        OOO00OO0O0OOOOOO0 ._age_net =None #line:14
        OOO00OO0O0OOOOOO0 ._gender_net =None #line:15
        OOO00OO0O0OOOOOO0 ._face_detector =FaceDetector ()#line:16
        OOO00OO0O0OOOOOO0 ._clear ()#line:17
    def _clear (OOO00OOOO000O000O ):#line:19
        OOO00OOOO000O000O ._age_index =-1 #line:20
        OOO00OOOO000O000O ._age_label =''#line:21
        OOO00OOOO000O000O ._age_confidence =0 #line:22
        OOO00OOOO000O000O ._gender_index =-1 #line:23
        OOO00OOOO000O000O ._gender_label =''#line:24
        OOO00OOOO000O000O ._gender_confidence =0 #line:25
    def load_age_model (OO0O0OOOOO000O000 ,folder =None ):#line:27
        try :#line:28
            if folder is None :#line:29
                folder =AgeGenderDetector ._DEFAULT_FOLDER #line:30
            OOOO0000OO0OOOOO0 =os .path .join (folder ,'age.caffemodel')#line:31
            if os .path .exists (OOOO0000OO0OOOOO0 ):#line:32
                OO0O0OOOOO000O000 ._age_net =cv2 .dnn .readNet (OOOO0000OO0OOOOO0 ,os .path .join (folder ,'age.prototxt'))#line:33
            else :#line:34
                OO0O0OOOOO000O000 ._age_net =cv2 .dnn .readNet (folder +'.caffemodel',folder +'.prototxt')#line:35
            return True #line:36
        except :#line:37
            return False #line:38
    def download_age_model (O0O00O0OOO00OOO0O ,folder =None ,overwrite =False ):#line:40
        print ('model downloading...')#line:41
        if folder is None :#line:42
            folder =AgeGenderDetector ._DEFAULT_FOLDER #line:43
        if not os .path .isdir (folder ):#line:44
            os .makedirs (folder )#line:45
        DownloadTool .download_model (folder ,'age.caffemodel',overwrite )#line:46
        DownloadTool .download_model (folder ,'age.prototxt',overwrite )#line:47
    def load_gender_model (O00O00O0O0OOOOOOO ,folder =None ):#line:49
        try :#line:50
            if folder is None :#line:51
                folder =AgeGenderDetector ._DEFAULT_FOLDER #line:52
            OO0OOO00OOOO0OOOO =os .path .join (folder ,'gender.caffemodel')#line:53
            if os .path .exists (OO0OOO00OOOO0OOOO ):#line:54
                O00O00O0O0OOOOOOO ._gender_net =cv2 .dnn .readNet (OO0OOO00OOOO0OOOO ,os .path .join (folder ,'gender.prototxt'))#line:55
            else :#line:56
                O00O00O0O0OOOOOOO ._gender_net =cv2 .dnn .readNet (folder +'.caffemodel',folder +'.prototxt')#line:57
            return True #line:58
        except :#line:59
            return False #line:60
    def download_gender_model (O00O00OO00O0O0O00 ,folder =None ,overwrite =False ):#line:62
        print ('model downloading...')#line:63
        if folder is None :#line:64
            folder =AgeGenderDetector ._DEFAULT_FOLDER #line:65
        if not os .path .isdir (folder ):#line:66
            os .makedirs (folder )#line:67
        DownloadTool .download_model (folder ,'gender.caffemodel',overwrite )#line:68
        DownloadTool .download_model (folder ,'gender.prototxt',overwrite )#line:69
    def detect (O0OOOOO0O0O0OOOOO ,OOO0O0OOO0OOOO0OO ,gpu =False ):#line:71
        if OOO0O0OOO0OOOO0OO is None :#line:72
            O0OOOOO0O0O0OOOOO ._clear ()#line:73
        elif O0OOOOO0O0O0OOOOO ._age_net is not None or O0OOOOO0O0O0OOOOO ._gender_net is not None :#line:74
            if O0OOOOO0O0O0OOOOO ._face_detector .detect (OOO0O0OOO0OOOO0OO ,padding =20 ):#line:75
                OO00O00O0O0OO00O0 =O0OOOOO0O0O0OOOOO ._face_detector .crop (OOO0O0OOO0OOOO0OO )#line:76
                if OO00O00O0O0OO00O0 is None :#line:77
                    O0OOOOO0O0O0OOOOO ._clear ()#line:78
                else :#line:79
                    O0000O0OO0OOO0OO0 =cv2 .dnn .blobFromImage (OO00O00O0O0OO00O0 ,1.0 ,(227 ,227 ),AgeGenderDetector ._MODEL_MEAN_VALUES ,swapRB =False )#line:80
                    if gpu :#line:81
                        O0OOOOO0O0O0OOOOO ._age_net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:82
                        O0OOOOO0O0O0OOOOO ._age_net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:83
                    if O0OOOOO0O0O0OOOOO ._age_net is not None :#line:84
                        O0OOOOO0O0O0OOOOO ._age_net .setInput (O0000O0OO0OOO0OO0 )#line:85
                        O0O000O000O0O0O0O =O0OOOOO0O0O0OOOOO ._age_net .forward ()[0 ]#line:86
                        O000OOO0OOOOO0OOO =O0O000O000O0O0O0O .argmax ()#line:87
                        O0OOOOO0O0O0OOOOO ._age_index =O000OOO0OOOOO0OOO #line:88
                        O0OOOOO0O0O0OOOOO ._age_label =AgeGenderDetector ._AGE_LABELS [O000OOO0OOOOO0OOO ]#line:89
                        O0OOOOO0O0O0OOOOO ._age_confidence =O0O000O000O0O0O0O [O000OOO0OOOOO0OOO ]#line:90
                    if O0OOOOO0O0O0OOOOO ._gender_net is not None :#line:91
                        O0OOOOO0O0O0OOOOO ._gender_net .setInput (O0000O0OO0OOO0OO0 )#line:92
                        O0O000O000O0O0O0O =O0OOOOO0O0O0OOOOO ._gender_net .forward ()[0 ]#line:93
                        O000OOO0OOOOO0OOO =O0O000O000O0O0O0O .argmax ()#line:94
                        O0OOOOO0O0O0OOOOO ._gender_index =O000OOO0OOOOO0OOO #line:95
                        O0OOOOO0O0O0OOOOO ._gender_label =AgeGenderDetector ._GENDER_LABELS [O000OOO0OOOOO0OOO ]#line:96
                        O0OOOOO0O0O0OOOOO ._gender_confidence =O0O000O000O0O0O0O [O000OOO0OOOOO0OOO ]#line:97
                    return True #line:98
            else :#line:99
                O0OOOOO0O0O0OOOOO ._clear ()#line:100
        return False #line:101
    def draw_result (OOOOOO0OO00OO0OO0 ,O00O0000000OO000O ,color =(0 ,255 ,0 ),thickness =2 ,clone =False ):#line:103
        if O00O0000000OO000O is not None :#line:104
            if clone :#line:105
                O00O0000000OO000O =O00O0000000OO000O .copy ()#line:106
            O000OO000O00OO00O =OOOOOO0OO00OO0OO0 ._face_detector .get_box ()#line:107
            if O000OO000O00OO00O is not None :#line:108
                cv2 .rectangle (O00O0000000OO000O ,(O000OO000O00OO00O [0 ],O000OO000O00OO00O [1 ]),(O000OO000O00OO00O [2 ],O000OO000O00OO00O [3 ]),color ,thickness )#line:109
                if OOOOOO0OO00OO0OO0 ._age_net is not None and OOOOOO0OO00OO0OO0 ._gender_net is not None :#line:110
                    OOOO00000O0O000OO ='{}, {}'.format (OOOOOO0OO00OO0OO0 ._age_label ,OOOOOO0OO00OO0OO0 ._gender_label )#line:111
                elif OOOOOO0OO00OO0OO0 ._age_net is not None :#line:112
                    OOOO00000O0O000OO =OOOOOO0OO00OO0OO0 ._age_label #line:113
                elif OOOOOO0OO00OO0OO0 ._gender_net is not None :#line:114
                    OOOO00000O0O000OO =OOOOOO0OO00OO0OO0 ._gender_label #line:115
                else :#line:116
                    OOOO00000O0O000OO =''#line:117
                cv2 .putText (O00O0000000OO000O ,OOOO00000O0O000OO ,(O000OO000O00OO00O [0 ],O000OO000O00OO00O [1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,color ,thickness )#line:118
        return O00O0000000OO000O #line:119
    def get_age_index (OO0OO00000O00O00O ):#line:121
        return OO0OO00000O00O00O ._age_index #line:122
    def get_age_label (O000O0O0O0O000O00 ):#line:124
        return O000O0O0O0O000O00 ._age_label #line:125
    def get_age_conf (O00O00O0000OO0000 ):#line:127
        return O00O00O0000OO0000 ._age_confidence #line:128
    def get_gender_index (O0000OO0O0OO00OOO ):#line:130
        return O0000OO0O0OO00OOO ._gender_index #line:131
    def get_gender_label (OO00OOOOOOO00O000 ):#line:133
        return OO00OOOOOOO00O000 ._gender_label #line:134
    def get_gender_conf (OOOOOO000OO0O0OO0 ):#line:136
        return OOOOOO000OO0O0OO0 ._gender_confidence #line:137
