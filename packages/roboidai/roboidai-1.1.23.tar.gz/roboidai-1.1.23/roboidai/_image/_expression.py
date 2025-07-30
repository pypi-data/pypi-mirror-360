import cv2 #line:1
import numpy as np #line:2
from PIL import Image ,ImageDraw #line:3
from ._util import FontUtil #line:4
_O0O000000OOO00000 ={'en':{'angry':'angry','disgust':'disgust','fear':'fear','happy':'happy','sad':'sad','surprise':'surprise','neutral':'neutral'},'ko':{'angry':'화남','disgust':'혐오','fear':'두려움','happy':'행복','sad':'슬픔','surprise':'놀람','neutral':'무표정'}}#line:26
class FacialExpression :#line:29
    def __init__ (O000OO00O000O0O00 ,lang ='en'):#line:30
        if lang in _O0O000000OOO00000 :#line:31
            O000OO00O000O0O00 ._labels =_O0O000000OOO00000 [lang ]#line:32
        else :#line:33
            O000OO00O000O0O00 ._labels =_O0O000000OOO00000 ['en']#line:34
        O000OO00O000O0O00 ._model =None #line:35
        O000OO00O000O0O00 ._clear ()#line:36
    def _clear (OOO0OOOO0OO0O0O0O ):#line:38
        OOO0OOOO0OO0O0O0O ._box =None #line:39
        OOO0OOOO0OO0O0O0O ._label =''#line:40
        OOO0OOOO0OO0O0O0O ._confidence =0 #line:41
    def load_model (O0OO000OO000OOO00 ):#line:43
        if O0OO000OO000OOO00 ._model is not None :return True #line:44
        try :#line:45
            from fer import FER #line:46
            O0OO000OO000OOO00 ._model =FER (mtcnn =True )#line:47
            return True #line:48
        except :#line:49
            return False #line:50
    def detect (OOO0000OO0O0OOOO0 ,OOOO00O00O00000O0 ):#line:52
        if OOOO00O00O00000O0 is not None and OOO0000OO0O0OOOO0 ._model is not None :#line:53
            O0O00OO0O0O0OOO00 =OOO0000OO0O0OOOO0 ._model .detect_emotions (OOOO00O00O00000O0 )#line:54
            if O0O00OO0O0O0OOO00 and len (O0O00OO0O0O0OOO00 )>0 :#line:55
                OOO000O000OO00000 =[max (OO00OO00O0O0O0000 ["emotions"],key =lambda OOO0O0OOOO0000OOO :OO00OO00O0O0O0000 ["emotions"][OOO0O0OOOO0000OOO ])for OO00OO00O0O0O0000 in O0O00OO0O0O0OOO00 ]#line:58
                O0OO00OOOOO0OOOO0 =OOO000O000OO00000 [0 ]#line:59
                OOO0000OO0O0OOOO0 ._confidence =O0O00OO0O0O0OOO00 [0 ]["emotions"][O0OO00OOOOO0OOOO0 ]#line:60
                O00OO0OO000OO00OO =np .array (O0O00OO0O0O0OOO00 [0 ]['box'])#line:61
                O00OO0OO000OO00OO [2 ]+=O00OO0OO000OO00OO [0 ]#line:62
                O00OO0OO000OO00OO [3 ]+=O00OO0OO000OO00OO [1 ]#line:63
                OOO0000OO0O0OOOO0 ._box =O00OO0OO000OO00OO #line:64
                OOO0000OO0O0OOOO0 ._label =OOO0000OO0O0OOOO0 ._labels [O0OO00OOOOO0OOOO0 ]#line:65
                return True #line:66
        OOO0000OO0O0OOOO0 ._clear ()#line:67
        return False #line:68
    def draw_result (O00000O0O0000O0OO ,O0OOO00OO0000OO0O ,color =(0 ,255 ,0 ),thickness =2 ,show_conf =False ,clone =False ):#line:70
        if O0OOO00OO0000OO0O is not None :#line:71
            if clone :#line:72
                O0OOO00OO0000OO0O =O0OOO00OO0000OO0O .copy ()#line:73
            O000000OOOOO00OOO =O00000O0O0000O0OO ._box #line:74
            if O000000OOOOO00OOO is not None :#line:75
                cv2 .rectangle (O0OOO00OO0000OO0O ,(O000000OOOOO00OOO [0 ],O000000OOOOO00OOO [1 ]),(O000000OOOOO00OOO [2 ],O000000OOOOO00OOO [3 ]),color ,thickness )#line:76
                O0O0OO0O000O0OOOO =O00000O0O0000O0OO ._label #line:77
                if show_conf :#line:78
                    O0O0OO0O000O0OOOO +=' '+str (format (O00000O0O0000O0OO ._confidence *100 ,'.0f'))+'%'#line:79
                O0O0O0OOO0O00OO0O =Image .fromarray (O0OOO00OO0000OO0O )#line:80
                O000OOO0O0O00O00O =ImageDraw .Draw (O0O0O0OOO0O00OO0O )#line:81
                O000OOO0O0O00O00O .text ((O000000OOOOO00OOO [0 ],O000000OOOOO00OOO [1 ]-20 ),O0O0OO0O000O0OOOO ,font =FontUtil .get_font (),fill =color )#line:82
                return np .asarray (O0O0O0OOO0O00OO0O )#line:83
        return O0OOO00OO0000OO0O #line:84
    def get_box (OO0OOOOOO000O0OO0 ):#line:86
        return OO0OOOOOO000O0OO0 ._box #line:87
    def get_label (OOOO000OO0OOO0000 ):#line:89
        return OOOO000OO0OOO0000 ._label #line:90
    def get_conf (OO0O00OOO00O0OO0O ):#line:92
        return OO0O00OOO00O0OO0O ._confidence #line:93
