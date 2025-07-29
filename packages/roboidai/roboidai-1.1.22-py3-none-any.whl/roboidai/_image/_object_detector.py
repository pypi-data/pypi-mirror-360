import cv2 #line:2
import os #line:3
import numpy as np #line:4
from PIL import Image ,ImageDraw #line:8
from ._tool import DownloadTool #line:9
from ._util import FontUtil #line:10
initialize =True #line:12
net =None #line:13
classes =None #line:15
COLORS =np .random .uniform (0 ,255 ,size =(80 ,3 ))#line:16
_O00000O00OO0000O0 ={'en':['person','bicycle','car','motorcycle','airplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','couch','potted plant','bed','dining table','toilet','tv','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush'],'ko':['사람','자전거','자동차','오토바이','비행기','버스','기차','트럭','배','신호등','소화전','정지 신호','주차 미터기','벤치','새','고양이','개','말','양','소','코끼리','곰','얼룩말','기린','배낭','우산','핸드백','넥타이','여행 가방','원반','스키','스노보드','공','연','야구 방망이','야구 글러브','스케이트보드','서프보드','테니스 채','병','포도주 잔','컵','포크','칼','숟가락','그릇','바나나','사과','샌드위치','오렌지','브로콜리','당근','핫도그','피자','도넛','케이크','의자','소파','화분','침대','식탁','변기','텔레비전','노트북','마우스','리모컨','키보드','휴대 전화','전자레인지','오븐','토스터','싱크대','냉장고','책','시계','꽃병','가위','곰 인형','헤어드라이어','칫솔']}#line:38
def populate_class_labels (O00OO000O0000OO00 ):#line:40
    if O00OO000O0000OO00 in _O00000O00OO0000O0 :#line:52
        O0000O000O0000O0O =_O00000O00OO0000O0 [O00OO000O0000OO00 ]#line:53
    else :#line:54
        O0000O000O0000O0O =_O00000O00OO0000O0 ['en']#line:55
    return O0000O000O0000O0O #line:56
def get_output_layers (OOO00O000OOO0O0OO ):#line:59
    OOOO00OO00O000OO0 =OOO00O000OOO0O0OO .getLayerNames ()#line:61
    OOOO0000OO000000O =OOO00O000OOO0O0OO .getUnconnectedOutLayers ()#line:62
    try :#line:63
        O00O00OO000O0O000 =[OOOO00OO00O000OO0 [O000000O000OOOO0O -1 ]for O000000O000OOOO0O in OOOO0000OO000000O ]#line:64
    except :#line:65
        O00O00OO000O0O000 =[OOOO00OO00O000OO0 [O0OO0000O0000OOOO [0 ]-1 ]for O0OO0000O0000OOOO in OOOO0000OO000000O ]#line:66
    return O00O00OO000O0O000 #line:68
def draw_bbox (O0OOO00O0O00O00OO ,O00OOOO0000OOOO00 ,OO0O00OOOOOO0O000 ,OO0000O0O0O000O0O ,OO000OOOOO0O000O0 ,colors =None ,write_conf =False ):#line:71
    global COLORS #line:73
    global classes #line:74
    if classes is None :#line:76
        classes =populate_class_labels (O00OOOO0000OOOO00 )#line:77
    if colors is None :#line:79
        colors =COLORS #line:80
    _OOO0O0OOOO0O00000 =FontUtil .get_font ()#line:82
    if isinstance (OO0000O0O0O000O0O ,str ):#line:83
        O00OOOOO00O0OOO00 =colors [0 ]#line:84
        if write_conf :#line:85
            OO0000O0O0O000O0O +=' '+str (format (OO000OOOOO0O000O0 *100 ,'.2f'))+'%'#line:86
        cv2 .rectangle (O0OOO00O0O00O00OO ,(OO0O00OOOOOO0O000 [0 ],OO0O00OOOOOO0O000 [1 ]),(OO0O00OOOOOO0O000 [2 ],OO0O00OOOOOO0O000 [3 ]),O00OOOOO00O0OOO00 ,2 )#line:87
        OO000O00O0OO0OOO0 =Image .fromarray (O0OOO00O0O00O00OO )#line:88
        O00O0O0O00OO000O0 =ImageDraw .Draw (OO000O00O0OO0OOO0 )#line:89
        O00OOOOO00O0OOO00 =(int (O00OOOOO00O0OOO00 [0 ]),int (O00OOOOO00O0OOO00 [1 ]),int (O00OOOOO00O0OOO00 [2 ]))#line:90
        O00O0O0O00OO000O0 .text ((OO0O00OOOOOO0O000 [0 ],OO0O00OOOOOO0O000 [1 ]-20 ),OO0000O0O0O000O0O ,font =_OOO0O0OOOO0O00000 ,fill =O00OOOOO00O0OOO00 )#line:91
    else :#line:93
        for OO0OOOOO0OOOOO0O0 ,O0O0OOOOO0OOOO0OO in enumerate (OO0000O0O0O000O0O ):#line:94
            O00OOOOO00O0OOO00 =colors [classes .index (O0O0OOOOO0OOOO0OO )]#line:95
            cv2 .rectangle (O0OOO00O0O00O00OO ,(OO0O00OOOOOO0O000 [OO0OOOOO0OOOOO0O0 ][0 ],OO0O00OOOOOO0O000 [OO0OOOOO0OOOOO0O0 ][1 ]),(OO0O00OOOOOO0O000 [OO0OOOOO0OOOOO0O0 ][2 ],OO0O00OOOOOO0O000 [OO0OOOOO0OOOOO0O0 ][3 ]),O00OOOOO00O0OOO00 ,2 )#line:96
        OO000O00O0OO0OOO0 =Image .fromarray (O0OOO00O0O00O00OO )#line:97
        O00O0O0O00OO000O0 =ImageDraw .Draw (OO000O00O0OO0OOO0 )#line:98
        for OO0OOOOO0OOOOO0O0 ,O0O0OOOOO0OOOO0OO in enumerate (OO0000O0O0O000O0O ):#line:99
            O00OOOOO00O0OOO00 =colors [classes .index (O0O0OOOOO0OOOO0OO )]#line:100
            O00OOOOO00O0OOO00 =(int (O00OOOOO00O0OOO00 [0 ]),int (O00OOOOO00O0OOO00 [1 ]),int (O00OOOOO00O0OOO00 [2 ]))#line:101
            if write_conf :#line:102
                O0O0OOOOO0OOOO0OO +=' '+str (format (OO000OOOOO0O000O0 [OO0OOOOO0OOOOO0O0 ]*100 ,'.2f'))+'%'#line:103
            O00O0O0O00OO000O0 .text ((OO0O00OOOOOO0O000 [OO0OOOOO0OOOOO0O0 ][0 ],OO0O00OOOOOO0O000 [OO0OOOOO0OOOOO0O0 ][1 ]-20 ),O0O0OOOOO0OOOO0OO ,font =_OOO0O0OOOO0O00000 ,fill =O00OOOOO00O0OOO00 )#line:104
    return np .asarray (OO000O00O0OO0OOO0 )#line:107
def detect_common_objects (O000000O0OO0OO0O0 ,OOOO00OOO0000O000 ,confidence =0.5 ,nms_thresh =0.3 ,enable_gpu =False ):#line:110
    OOO0OO00000OO00OO ,O00O0O00O0O00O000 =O000000O0OO0OO0O0 .shape [:2 ]#line:112
    O0O0O0000O00000O0 =0.00392 #line:113
    global classes #line:115
    O000OOOOO000OO00O =cv2 .dnn .blobFromImage (O000000O0OO0OO0O0 ,O0O0O0000O00000O0 ,(416 ,416 ),(0 ,0 ,0 ),True ,crop =False )#line:131
    global initialize #line:142
    global net #line:143
    if initialize :#line:145
        classes =populate_class_labels (OOOO00OOO0000O000 )#line:146
        initialize =False #line:148
    if enable_gpu :#line:151
        net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:152
        net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:153
    net .setInput (O000OOOOO000OO00O )#line:155
    OOO0OO00O000OO00O =net .forward (get_output_layers (net ))#line:157
    O0OOOOOOO0OO0O0O0 =[]#line:159
    OOOO000O0OOOO00O0 =[]#line:160
    OOOOOOO0OOOOO0O0O =[]#line:161
    for OOO0O0000OOO0O00O in OOO0OO00O000OO00O :#line:163
        for O0OO0O00000OOOOOO in OOO0O0000OOO0O00O :#line:164
            O00000OO0O000OO00 =O0OO0O00000OOOOOO [5 :]#line:165
            OOO00O0O00O0OOOO0 =np .argmax (O00000OO0O000OO00 )#line:166
            OOO00000OOOOOO0O0 =O00000OO0O000OO00 [OOO00O0O00O0OOOO0 ]#line:167
            if OOO00000OOOOOO0O0 >confidence :#line:168
                O0O000OO000O0OO00 =int (O0OO0O00000OOOOOO [0 ]*O00O0O00O0O00O000 )#line:169
                OOOOO0OOO0OO000O0 =int (O0OO0O00000OOOOOO [1 ]*OOO0OO00000OO00OO )#line:170
                O0O00000O0OOO0OO0 =int (O0OO0O00000OOOOOO [2 ]*O00O0O00O0O00O000 )#line:171
                O0OOO0OOOO00O0OOO =int (O0OO0O00000OOOOOO [3 ]*OOO0OO00000OO00OO )#line:172
                OOO0OOOO0O0OOOO00 =O0O000OO000O0OO00 -(O0O00000O0OOO0OO0 /2 )#line:173
                OOOOO0OOO00O00O0O =OOOOO0OOO0OO000O0 -(O0OOO0OOOO00O0OOO /2 )#line:174
                O0OOOOOOO0OO0O0O0 .append (OOO00O0O00O0OOOO0 )#line:175
                OOOO000O0OOOO00O0 .append (float (OOO00000OOOOOO0O0 ))#line:176
                OOOOOOO0OOOOO0O0O .append ([OOO0OOOO0O0OOOO00 ,OOOOO0OOO00O00O0O ,O0O00000O0OOO0OO0 ,O0OOO0OOOO00O0OOO ])#line:177
    O000O000O0O000O00 =cv2 .dnn .NMSBoxes (OOOOOOO0OOOOO0O0O ,OOOO000O0OOOO00O0 ,confidence ,nms_thresh )#line:180
    O0000O0O00O0O0O0O =[]#line:182
    O00OOOOO0OO0O0OO0 =[]#line:183
    OOO00000O0O000O00 =[]#line:184
    try :#line:186
        for O0OOOOO0OO0000000 in O000O000O0O000O00 :#line:187
            OO000OOOOOOOO000O =OOOOOOO0OOOOO0O0O [O0OOOOO0OO0000000 ]#line:189
            OOO0OOOO0O0OOOO00 =OO000OOOOOOOO000O [0 ]#line:190
            OOOOO0OOO00O00O0O =OO000OOOOOOOO000O [1 ]#line:191
            O0O00000O0OOO0OO0 =OO000OOOOOOOO000O [2 ]#line:192
            O0OOO0OOOO00O0OOO =OO000OOOOOOOO000O [3 ]#line:193
            O0000O0O00O0O0O0O .append ([int (OOO0OOOO0O0OOOO00 ),int (OOOOO0OOO00O00O0O ),int (OOO0OOOO0O0OOOO00 +O0O00000O0OOO0OO0 ),int (OOOOO0OOO00O00O0O +O0OOO0OOOO00O0OOO )])#line:194
            O00OOOOO0OO0O0OO0 .append (str (classes [O0OOOOOOO0OO0O0O0 [O0OOOOO0OO0000000 ]]))#line:195
            OOO00000O0O000O00 .append (OOOO000O0OOOO00O0 [O0OOOOO0OO0000000 ])#line:196
    except :#line:197
        for O0OOOOO0OO0000000 in O000O000O0O000O00 :#line:198
            O0OOOOO0OO0000000 =O0OOOOO0OO0000000 [0 ]#line:199
            OO000OOOOOOOO000O =OOOOOOO0OOOOO0O0O [O0OOOOO0OO0000000 ]#line:200
            OOO0OOOO0O0OOOO00 =OO000OOOOOOOO000O [0 ]#line:201
            OOOOO0OOO00O00O0O =OO000OOOOOOOO000O [1 ]#line:202
            O0O00000O0OOO0OO0 =OO000OOOOOOOO000O [2 ]#line:203
            O0OOO0OOOO00O0OOO =OO000OOOOOOOO000O [3 ]#line:204
            O0000O0O00O0O0O0O .append ([int (OOO0OOOO0O0OOOO00 ),int (OOOOO0OOO00O00O0O ),int (OOO0OOOO0O0OOOO00 +O0O00000O0OOO0OO0 ),int (OOOOO0OOO00O00O0O +O0OOO0OOOO00O0OOO )])#line:205
            O00OOOOO0OO0O0OO0 .append (str (classes [O0OOOOOOO0OO0O0O0 [O0OOOOO0OO0000000 ]]))#line:206
            OOO00000O0O000O00 .append (OOOO000O0OOOO00O0 [O0OOOOO0OO0000000 ])#line:207
    return O0000O0O00O0O0O0O ,O00OOOOO0OO0O0OO0 ,OOO00000O0O000O00 #line:209
def load_common_objects_model (O0O00000O00O000OO ,O0OOO00OO0O0000OO ):#line:211
    global net #line:212
    try :#line:213
        net =cv2 .dnn .readNet (O0O00000O00O000OO ,O0OOO00OO0O0000OO )#line:214
        return True #line:215
    except :#line:216
        return False #line:217
class YOLO :#line:220
    def __init__ (OOOO0OOOOOO000OO0 ,O0OOOOO00000OOO0O ,OO00O0O0O0OOO0O00 ,OO0O000O0O000OOOO ,version ='yolov3'):#line:222
        print ('[INFO] Initializing YOLO ..')#line:224
        OOOO0OOOOOO000OO0 .config =OO00O0O0O0OOO0O00 #line:226
        OOOO0OOOOOO000OO0 .weights =O0OOOOO00000OOO0O #line:227
        OOOO0OOOOOO000OO0 .version =version #line:228
        with open (OO0O000O0O000OOOO ,'r')as O0O0O0O00O0O0OOO0 :#line:230
            OOOO0OOOOOO000OO0 .labels =[OO00O00OO00O0O000 .strip ()for OO00O00OO00O0O000 in O0O0O0O00O0O0OOO0 .readlines ()]#line:231
        OOOO0OOOOOO000OO0 .colors =np .random .uniform (0 ,255 ,size =(len (OOOO0OOOOOO000OO0 .labels ),3 ))#line:233
        OOOO0OOOOOO000OO0 .net =cv2 .dnn .readNet (OOOO0OOOOOO000OO0 .weights ,OOOO0OOOOOO000OO0 .config )#line:235
        O00O00O0O0O00O0O0 =OOOO0OOOOOO000OO0 .net .getLayerNames ()#line:237
        OOOO0OOOOOO000OO0 .output_layers =[O00O00O0O0O00O0O0 [OOO0O0OO000OOO0O0 [0 ]-1 ]for OOO0O0OO000OOO0O0 in OOOO0OOOOOO000OO0 .net .getUnconnectedOutLayers ()]#line:239
    def detect_objects (O0O000O00000O0O00 ,OOO000O00O000OO0O ,confidence =0.5 ,nms_thresh =0.3 ,enable_gpu =False ):#line:243
        if enable_gpu :#line:245
            net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:246
            net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:247
        OO0OOO0O00OO0OOOO ,O0OO0O0OO000O0O0O =OOO000O00O000OO0O .shape [:2 ]#line:249
        OO00OO0O0O0O000O0 =0.00392 #line:250
        O0OO0O000OO000000 =cv2 .dnn .blobFromImage (OOO000O00O000OO0O ,OO00OO0O0O0O000O0 ,(416 ,416 ),(0 ,0 ,0 ),True ,crop =False )#line:253
        O0O000O00000O0O00 .net .setInput (O0OO0O000OO000000 )#line:255
        O0OOO0O0O00OOO00O =O0O000O00000O0O00 .net .forward (O0O000O00000O0O00 .output_layers )#line:257
        OO0OO0OOOO0O0000O =[]#line:259
        OO0OO0OOO000O00OO =[]#line:260
        OOO00OOOO00OOO0O0 =[]#line:261
        for O00OO000OOO00OOO0 in O0OOO0O0O00OOO00O :#line:263
            for OO000OO0OOOOO000O in O00OO000OOO00OOO0 :#line:264
                OOO0O00000O00OO0O =OO000OO0OOOOO000O [5 :]#line:265
                O0OO0OO00OO0000OO =np .argmax (OOO0O00000O00OO0O )#line:266
                OOO000000000OO00O =OOO0O00000O00OO0O [O0OO0OO00OO0000OO ]#line:267
                if OOO000000000OO00O >confidence :#line:268
                    OO0OOO0OOOO0OO000 =int (OO000OO0OOOOO000O [0 ]*O0OO0O0OO000O0O0O )#line:269
                    OO0000O0O00OO0OOO =int (OO000OO0OOOOO000O [1 ]*OO0OOO0O00OO0OOOO )#line:270
                    O00OO0OOO000000OO =int (OO000OO0OOOOO000O [2 ]*O0OO0O0OO000O0O0O )#line:271
                    O0O0OO0OOOOO0OO0O =int (OO000OO0OOOOO000O [3 ]*OO0OOO0O00OO0OOOO )#line:272
                    O0OOO00OO0O000OOO =OO0OOO0OOOO0OO000 -(O00OO0OOO000000OO /2 )#line:273
                    O00O0000OO0000O00 =OO0000O0O00OO0OOO -(O0O0OO0OOOOO0OO0O /2 )#line:274
                    OO0OO0OOOO0O0000O .append (O0OO0OO00OO0000OO )#line:275
                    OO0OO0OOO000O00OO .append (float (OOO000000000OO00O ))#line:276
                    OOO00OOOO00OOO0O0 .append ([O0OOO00OO0O000OOO ,O00O0000OO0000O00 ,O00OO0OOO000000OO ,O0O0OO0OOOOO0OO0O ])#line:277
        OOOO00OO0O0OOOOOO =cv2 .dnn .NMSBoxes (OOO00OOOO00OOO0O0 ,OO0OO0OOO000O00OO ,confidence ,nms_thresh )#line:280
        OO0OOOOOO0O0OO0O0 =[]#line:282
        O00O0O00000OO000O =[]#line:283
        OOOO0OO00O00OOOO0 =[]#line:284
        for OO000O0OOOO000O0O in OOOO00OO0O0OOOOOO :#line:286
            OO000O0OOOO000O0O =OO000O0OOOO000O0O [0 ]#line:287
            OOOO0O0O0O00O0OO0 =OOO00OOOO00OOO0O0 [OO000O0OOOO000O0O ]#line:288
            O0OOO00OO0O000OOO =OOOO0O0O0O00O0OO0 [0 ]#line:289
            O00O0000OO0000O00 =OOOO0O0O0O00O0OO0 [1 ]#line:290
            O00OO0OOO000000OO =OOOO0O0O0O00O0OO0 [2 ]#line:291
            O0O0OO0OOOOO0OO0O =OOOO0O0O0O00O0OO0 [3 ]#line:292
            OO0OOOOOO0O0OO0O0 .append ([int (O0OOO00OO0O000OOO ),int (O00O0000OO0000O00 ),int (O0OOO00OO0O000OOO +O00OO0OOO000000OO ),int (O00O0000OO0000O00 +O0O0OO0OOOOO0OO0O )])#line:293
            O00O0O00000OO000O .append (str (O0O000O00000O0O00 .labels [OO0OO0OOOO0O0000O [OO000O0OOOO000O0O ]]))#line:294
            OOOO0OO00O00OOOO0 .append (OO0OO0OOO000O00OO [OO000O0OOOO000O0O ])#line:295
        return OO0OOOOOO0O0OO0O0 ,O00O0O00000OO000O ,OOOO0OO00O00OOOO0 #line:297
    def draw_bbox (OOOOO0O0O0O000000 ,O000O0OO00O0O0O00 ,O000OOOOOOOO00O0O ,O0OOO0OO0O0OO0O00 ,O00OOOOOOO0000000 ,colors =None ,write_conf =False ):#line:300
        if colors is None :#line:302
            colors =OOOOO0O0O0O000000 .colors #line:303
        if isinstance (O0OOO0OO0O0OO0O00 ,list ):#line:305
            for O0OO0O0OO00OO0O00 ,OO0OOOO00OOO0O0OO in enumerate (O0OOO0OO0O0OO0O00 ):#line:306
                O0000O00OOOOO0OOO =colors [OOOOO0O0O0O000000 .labels .index (OO0OOOO00OOO0O0OO )]#line:308
                if write_conf :#line:310
                    OO0OOOO00OOO0O0OO +=' '+str (format (O00OOOOOOO0000000 [O0OO0O0OO00OO0O00 ]*100 ,'.2f'))+'%'#line:311
                cv2 .rectangle (O000O0OO00O0O0O00 ,(O000OOOOOOOO00O0O [O0OO0O0OO00OO0O00 ][0 ],O000OOOOOOOO00O0O [O0OO0O0OO00OO0O00 ][1 ]),(O000OOOOOOOO00O0O [O0OO0O0OO00OO0O00 ][2 ],O000OOOOOOOO00O0O [O0OO0O0OO00OO0O00 ][3 ]),O0000O00OOOOO0OOO ,2 )#line:313
                cv2 .putText (O000O0OO00O0O0O00 ,OO0OOOO00OOO0O0OO ,(O000OOOOOOOO00O0O [O0OO0O0OO00OO0O00 ][0 ],O000OOOOOOOO00O0O [O0OO0O0OO00OO0O00 ][1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,O0000O00OOOOO0OOO ,2 )#line:315
        else :#line:316
            O0000O00OOOOO0OOO =colors [0 ]#line:317
            if write_conf :#line:318
                O0OOO0OO0O0OO0O00 +=' '+str (format (O00OOOOOOO0000000 *100 ,'.2f'))+'%'#line:319
            cv2 .rectangle (O000O0OO00O0O0O00 ,(O000OOOOOOOO00O0O [0 ],O000OOOOOOOO00O0O [1 ]),(O000OOOOOOOO00O0O [2 ],O000OOOOOOOO00O0O [3 ]),O0000O00OOOOO0OOO ,2 )#line:320
            cv2 .putText (O000O0OO00O0O0O00 ,OO0OOOO00OOO0O0OO ,(O000OOOOOOOO00O0O [0 ],O000OOOOOOOO00O0O [1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,O0000O00OOOOO0OOO ,2 )#line:321
class ObjectDetector :#line:324
    _DEFAULT_FOLDER ='c:/roboid/model'#line:325
    def __init__ (OOOO0O000OO0000O0 ,multi =False ,lang ='en'):#line:327
        OOOO0O000OO0000O0 ._multi =multi #line:328
        OOOO0O000OO0000O0 ._lang =lang #line:329
        OOOO0O000OO0000O0 ._loaded =False #line:330
        OOOO0O000OO0000O0 ._clear ()#line:331
    def _clear (O0O00OO0OOO00000O ):#line:333
        if O0O00OO0OOO00000O ._multi :#line:334
            O0O00OO0OOO00000O ._boxes =[]#line:335
            O0O00OO0OOO00000O ._labels =[]#line:336
            O0O00OO0OOO00000O ._confidences =[]#line:337
        else :#line:338
            O0O00OO0OOO00000O ._boxes =None #line:339
            O0O00OO0OOO00000O ._labels =''#line:340
            O0O00OO0OOO00000O ._confidences =0 #line:341
    def load_model (O0O00OO00OO0O0OO0 ,folder =None ):#line:343
        try :#line:344
            if folder is None :#line:345
                folder =ObjectDetector ._DEFAULT_FOLDER #line:346
            O0OOO00OOO0OO000O =os .path .join (folder ,'object.weights')#line:347
            if os .path .exists (O0OOO00OOO0OO000O ):#line:348
                OO0O0O0000OO0OOO0 =os .path .join (folder ,'object.cfg')#line:349
            else :#line:350
                O0OOO00OOO0OO000O =folder +'.weights'#line:351
                OO0O0O0000OO0OOO0 =folder +'.cfg'#line:352
            if load_common_objects_model (O0OOO00OOO0OO000O ,OO0O0O0000OO0OOO0 ):#line:353
                O0O00OO00OO0O0OO0 ._loaded =True #line:354
                return True #line:355
            return False #line:356
        except :#line:357
            return False #line:358
    def download_model (OOO00O0OOO0OOOO0O ,folder =None ,overwrite =False ):#line:360
        print ('model downloading...')#line:361
        if folder is None :#line:362
            folder =ObjectDetector ._DEFAULT_FOLDER #line:363
        if not os .path .isdir (folder ):#line:364
            os .makedirs (folder )#line:365
        DownloadTool .download_model (folder ,'object.weights',overwrite )#line:366
        DownloadTool .download_model (folder ,'object.cfg',overwrite )#line:367
    def detect (O0OO0OOO0OOO0OOO0 ,OO0OOOO0OOOOOOOOO ,conf_threshold =0.5 ,nms_threshold =0.4 ,gpu =False ):#line:369
        if OO0OOOO0OOOOOOOOO is None :#line:370
            O0OO0OOO0OOO0OOO0 ._clear ()#line:371
        elif O0OO0OOO0OOO0OOO0 ._loaded :#line:372
            OO00O000O0OO0OOO0 ,OOOOOOO0OOOO00OOO ,O0O0OOO0O00OOO0OO =detect_common_objects (OO0OOOO0OOOOOOOOO ,O0OO0OOO0OOO0OOO0 ._lang ,conf_threshold ,nms_threshold ,gpu )#line:373
            if O0OO0OOO0OOO0OOO0 ._multi :#line:374
                O0OO0OOO0OOO0OOO0 ._boxes =OO00O000O0OO0OOO0 #line:375
                O0OO0OOO0OOO0OOO0 ._labels =OOOOOOO0OOOO00OOO #line:376
                O0OO0OOO0OOO0OOO0 ._confidences =O0O0OOO0O00OOO0OO #line:377
                return len (OOOOOOO0OOOO00OOO )>0 #line:378
            else :#line:379
                OO00O0OOOO0O000OO =-1 #line:380
                O0OOOO0000O00000O =-1 #line:381
                for OOOOO0000OOO0OO00 ,OOOOO00OOO00OO000 in enumerate (OO00O000O0OO0OOO0 ):#line:382
                    OOO000OOOO00000O0 =abs (OOOOO00OOO00OO000 [2 ]-OOOOO00OOO00OO000 [0 ])*abs (OOOOO00OOO00OO000 [3 ]-OOOOO00OOO00OO000 [1 ])#line:383
                    if OOO000OOOO00000O0 >OO00O0OOOO0O000OO :#line:384
                        OO00O0OOOO0O000OO =OOO000OOOO00000O0 #line:385
                        O0OOOO0000O00000O =OOOOO0000OOO0OO00 #line:386
                if O0OOOO0000O00000O <0 :#line:387
                    O0OO0OOO0OOO0OOO0 ._boxes =None #line:388
                    O0OO0OOO0OOO0OOO0 ._labels =''#line:389
                    O0OO0OOO0OOO0OOO0 ._confidences =0 #line:390
                else :#line:391
                    O0OO0OOO0OOO0OOO0 ._boxes =OO00O000O0OO0OOO0 [O0OOOO0000O00000O ]#line:392
                    O0OO0OOO0OOO0OOO0 ._labels =OOOOOOO0OOOO00OOO [O0OOOO0000O00000O ]#line:393
                    O0OO0OOO0OOO0OOO0 ._confidences =O0O0OOO0O00OOO0OO [O0OOOO0000O00000O ]#line:394
                    return True #line:395
        return False #line:396
    def draw_result (OOOOOO000OO00OOO0 ,OO00OO000O0O00OO0 ,colors =None ,show_conf =False ):#line:398
        if OO00OO000O0O00OO0 is not None :#line:399
            if OOOOOO000OO00OOO0 ._multi or OOOOOO000OO00OOO0 ._boxes is not None :#line:400
                OO00OO000O0O00OO0 =draw_bbox (OO00OO000O0O00OO0 ,OOOOOO000OO00OOO0 ._lang ,OOOOOO000OO00OOO0 ._boxes ,OOOOOO000OO00OOO0 ._labels ,OOOOOO000OO00OOO0 ._confidences ,colors ,show_conf )#line:401
        return OO00OO000O0O00OO0 #line:402
    def get_box (O00000OO00O0OO000 ):#line:404
        return O00000OO00O0OO000 ._boxes #line:405
    def get_label (O00O00O0O0000OOO0 ):#line:407
        return O00O00O0O0000OOO0 ._labels #line:408
    def get_conf (O00O0OO0O0O0OO0O0 ):#line:410
        return O00O0OO0O0O0OO0O0 ._confidences #line:411
