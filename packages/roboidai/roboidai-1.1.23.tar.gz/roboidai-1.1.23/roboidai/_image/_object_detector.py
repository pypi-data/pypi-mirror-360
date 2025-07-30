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
_OO0O0O00OOO0OOOO0 ={'en':['person','bicycle','car','motorcycle','airplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','couch','potted plant','bed','dining table','toilet','tv','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush'],'ko':['사람','자전거','자동차','오토바이','비행기','버스','기차','트럭','배','신호등','소화전','정지 신호','주차 미터기','벤치','새','고양이','개','말','양','소','코끼리','곰','얼룩말','기린','배낭','우산','핸드백','넥타이','여행 가방','원반','스키','스노보드','공','연','야구 방망이','야구 글러브','스케이트보드','서프보드','테니스 채','병','포도주 잔','컵','포크','칼','숟가락','그릇','바나나','사과','샌드위치','오렌지','브로콜리','당근','핫도그','피자','도넛','케이크','의자','소파','화분','침대','식탁','변기','텔레비전','노트북','마우스','리모컨','키보드','휴대 전화','전자레인지','오븐','토스터','싱크대','냉장고','책','시계','꽃병','가위','곰 인형','헤어드라이어','칫솔']}#line:38
def populate_class_labels (O0O000OO0O00O00O0 ):#line:40
    if O0O000OO0O00O00O0 in _OO0O0O00OOO0OOOO0 :#line:52
        OOOO0OO0O0O0OOOOO =_OO0O0O00OOO0OOOO0 [O0O000OO0O00O00O0 ]#line:53
    else :#line:54
        OOOO0OO0O0O0OOOOO =_OO0O0O00OOO0OOOO0 ['en']#line:55
    return OOOO0OO0O0O0OOOOO #line:56
def get_output_layers (O0OOO000O00000000 ):#line:59
    OO0O0000OO00O00O0 =O0OOO000O00000000 .getLayerNames ()#line:61
    OOO000O0O0OO0OOO0 =O0OOO000O00000000 .getUnconnectedOutLayers ()#line:62
    try :#line:63
        O00OO0OOO0OO0O0O0 =[OO0O0000OO00O00O0 [OOOO0OOO0000OO0O0 -1 ]for OOOO0OOO0000OO0O0 in OOO000O0O0OO0OOO0 ]#line:64
    except :#line:65
        O00OO0OOO0OO0O0O0 =[OO0O0000OO00O00O0 [O00O0OO000O0O0000 [0 ]-1 ]for O00O0OO000O0O0000 in OOO000O0O0OO0OOO0 ]#line:66
    return O00OO0OOO0OO0O0O0 #line:68
def draw_bbox (OOO00O00OO0OO0O0O ,O0O0000OO0000OOOO ,OO0O0OOOOOOOO0OO0 ,O0000OO00OO00O0O0 ,O0OOO000O00O00O0O ,colors =None ,write_conf =False ):#line:71
    global COLORS #line:73
    global classes #line:74
    if classes is None :#line:76
        classes =populate_class_labels (O0O0000OO0000OOOO )#line:77
    if colors is None :#line:79
        colors =COLORS #line:80
    _O0OO000000OO00OOO =FontUtil .get_font ()#line:82
    if isinstance (O0000OO00OO00O0O0 ,str ):#line:83
        OOOOO00OO00OOO0OO =colors [0 ]#line:84
        if write_conf :#line:85
            O0000OO00OO00O0O0 +=' '+str (format (O0OOO000O00O00O0O *100 ,'.2f'))+'%'#line:86
        cv2 .rectangle (OOO00O00OO0OO0O0O ,(OO0O0OOOOOOOO0OO0 [0 ],OO0O0OOOOOOOO0OO0 [1 ]),(OO0O0OOOOOOOO0OO0 [2 ],OO0O0OOOOOOOO0OO0 [3 ]),OOOOO00OO00OOO0OO ,2 )#line:87
        O0OOOO00O000OOO0O =Image .fromarray (OOO00O00OO0OO0O0O )#line:88
        O0OOO00O0O00000OO =ImageDraw .Draw (O0OOOO00O000OOO0O )#line:89
        OOOOO00OO00OOO0OO =(int (OOOOO00OO00OOO0OO [0 ]),int (OOOOO00OO00OOO0OO [1 ]),int (OOOOO00OO00OOO0OO [2 ]))#line:90
        O0OOO00O0O00000OO .text ((OO0O0OOOOOOOO0OO0 [0 ],OO0O0OOOOOOOO0OO0 [1 ]-20 ),O0000OO00OO00O0O0 ,font =_O0OO000000OO00OOO ,fill =OOOOO00OO00OOO0OO )#line:91
    else :#line:93
        for OO00OO0O0OO0000OO ,O000O0O0O00OOOO0O in enumerate (O0000OO00OO00O0O0 ):#line:94
            OOOOO00OO00OOO0OO =colors [classes .index (O000O0O0O00OOOO0O )]#line:95
            cv2 .rectangle (OOO00O00OO0OO0O0O ,(OO0O0OOOOOOOO0OO0 [OO00OO0O0OO0000OO ][0 ],OO0O0OOOOOOOO0OO0 [OO00OO0O0OO0000OO ][1 ]),(OO0O0OOOOOOOO0OO0 [OO00OO0O0OO0000OO ][2 ],OO0O0OOOOOOOO0OO0 [OO00OO0O0OO0000OO ][3 ]),OOOOO00OO00OOO0OO ,2 )#line:96
        O0OOOO00O000OOO0O =Image .fromarray (OOO00O00OO0OO0O0O )#line:97
        O0OOO00O0O00000OO =ImageDraw .Draw (O0OOOO00O000OOO0O )#line:98
        for OO00OO0O0OO0000OO ,O000O0O0O00OOOO0O in enumerate (O0000OO00OO00O0O0 ):#line:99
            OOOOO00OO00OOO0OO =colors [classes .index (O000O0O0O00OOOO0O )]#line:100
            OOOOO00OO00OOO0OO =(int (OOOOO00OO00OOO0OO [0 ]),int (OOOOO00OO00OOO0OO [1 ]),int (OOOOO00OO00OOO0OO [2 ]))#line:101
            if write_conf :#line:102
                O000O0O0O00OOOO0O +=' '+str (format (O0OOO000O00O00O0O [OO00OO0O0OO0000OO ]*100 ,'.2f'))+'%'#line:103
            O0OOO00O0O00000OO .text ((OO0O0OOOOOOOO0OO0 [OO00OO0O0OO0000OO ][0 ],OO0O0OOOOOOOO0OO0 [OO00OO0O0OO0000OO ][1 ]-20 ),O000O0O0O00OOOO0O ,font =_O0OO000000OO00OOO ,fill =OOOOO00OO00OOO0OO )#line:104
    return np .asarray (O0OOOO00O000OOO0O )#line:107
def detect_common_objects (O00O0O00OOO0OOOO0 ,O00OOOOO000OO0OOO ,confidence =0.5 ,nms_thresh =0.3 ,enable_gpu =False ):#line:110
    OOOOO0OO0OO0OO00O ,OOOOOO00OOOOO00OO =O00O0O00OOO0OOOO0 .shape [:2 ]#line:112
    O0OOO0OOO00O0OOOO =0.00392 #line:113
    global classes #line:115
    O00OO0OOOO000O00O =cv2 .dnn .blobFromImage (O00O0O00OOO0OOOO0 ,O0OOO0OOO00O0OOOO ,(416 ,416 ),(0 ,0 ,0 ),True ,crop =False )#line:131
    global initialize #line:142
    global net #line:143
    if initialize :#line:145
        classes =populate_class_labels (O00OOOOO000OO0OOO )#line:146
        initialize =False #line:148
    if enable_gpu :#line:151
        net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:152
        net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:153
    net .setInput (O00OO0OOOO000O00O )#line:155
    OOO0O0O0OO0O0O00O =net .forward (get_output_layers (net ))#line:157
    OO0O00O0000O00OO0 =[]#line:159
    OOO00O0O0O0O0000O =[]#line:160
    O00OO00OO0OO0O000 =[]#line:161
    for OO0OOOO0OOOO0O0OO in OOO0O0O0OO0O0O00O :#line:163
        for OO0OO00OO0O0O00OO in OO0OOOO0OOOO0O0OO :#line:164
            OOO00O000000000O0 =OO0OO00OO0O0O00OO [5 :]#line:165
            O0O00O00000OO00O0 =np .argmax (OOO00O000000000O0 )#line:166
            OO0OOOOO00O000O0O =OOO00O000000000O0 [O0O00O00000OO00O0 ]#line:167
            if OO0OOOOO00O000O0O >confidence :#line:168
                O0OOOOOO0OOOOOOO0 =int (OO0OO00OO0O0O00OO [0 ]*OOOOOO00OOOOO00OO )#line:169
                O000O0000OOOO000O =int (OO0OO00OO0O0O00OO [1 ]*OOOOO0OO0OO0OO00O )#line:170
                OO0000O0OO0OO0O0O =int (OO0OO00OO0O0O00OO [2 ]*OOOOOO00OOOOO00OO )#line:171
                OO0O0OO0OO00O0OO0 =int (OO0OO00OO0O0O00OO [3 ]*OOOOO0OO0OO0OO00O )#line:172
                OOOO0OO00O00O00OO =O0OOOOOO0OOOOOOO0 -(OO0000O0OO0OO0O0O /2 )#line:173
                O0OOO00O000O00OOO =O000O0000OOOO000O -(OO0O0OO0OO00O0OO0 /2 )#line:174
                OO0O00O0000O00OO0 .append (O0O00O00000OO00O0 )#line:175
                OOO00O0O0O0O0000O .append (float (OO0OOOOO00O000O0O ))#line:176
                O00OO00OO0OO0O000 .append ([OOOO0OO00O00O00OO ,O0OOO00O000O00OOO ,OO0000O0OO0OO0O0O ,OO0O0OO0OO00O0OO0 ])#line:177
    O00O0OO0000000O00 =cv2 .dnn .NMSBoxes (O00OO00OO0OO0O000 ,OOO00O0O0O0O0000O ,confidence ,nms_thresh )#line:180
    OOOO000OOO0000000 =[]#line:182
    OOOO000O0O0O00O00 =[]#line:183
    O00OO0000OO0O0O00 =[]#line:184
    try :#line:186
        for OOOO0OO0OOOOOOO00 in O00O0OO0000000O00 :#line:187
            OO0OOO0O0OO00O0OO =O00OO00OO0OO0O000 [OOOO0OO0OOOOOOO00 ]#line:189
            OOOO0OO00O00O00OO =OO0OOO0O0OO00O0OO [0 ]#line:190
            O0OOO00O000O00OOO =OO0OOO0O0OO00O0OO [1 ]#line:191
            OO0000O0OO0OO0O0O =OO0OOO0O0OO00O0OO [2 ]#line:192
            OO0O0OO0OO00O0OO0 =OO0OOO0O0OO00O0OO [3 ]#line:193
            OOOO000OOO0000000 .append ([int (OOOO0OO00O00O00OO ),int (O0OOO00O000O00OOO ),int (OOOO0OO00O00O00OO +OO0000O0OO0OO0O0O ),int (O0OOO00O000O00OOO +OO0O0OO0OO00O0OO0 )])#line:194
            OOOO000O0O0O00O00 .append (str (classes [OO0O00O0000O00OO0 [OOOO0OO0OOOOOOO00 ]]))#line:195
            O00OO0000OO0O0O00 .append (OOO00O0O0O0O0000O [OOOO0OO0OOOOOOO00 ])#line:196
    except :#line:197
        for OOOO0OO0OOOOOOO00 in O00O0OO0000000O00 :#line:198
            OOOO0OO0OOOOOOO00 =OOOO0OO0OOOOOOO00 [0 ]#line:199
            OO0OOO0O0OO00O0OO =O00OO00OO0OO0O000 [OOOO0OO0OOOOOOO00 ]#line:200
            OOOO0OO00O00O00OO =OO0OOO0O0OO00O0OO [0 ]#line:201
            O0OOO00O000O00OOO =OO0OOO0O0OO00O0OO [1 ]#line:202
            OO0000O0OO0OO0O0O =OO0OOO0O0OO00O0OO [2 ]#line:203
            OO0O0OO0OO00O0OO0 =OO0OOO0O0OO00O0OO [3 ]#line:204
            OOOO000OOO0000000 .append ([int (OOOO0OO00O00O00OO ),int (O0OOO00O000O00OOO ),int (OOOO0OO00O00O00OO +OO0000O0OO0OO0O0O ),int (O0OOO00O000O00OOO +OO0O0OO0OO00O0OO0 )])#line:205
            OOOO000O0O0O00O00 .append (str (classes [OO0O00O0000O00OO0 [OOOO0OO0OOOOOOO00 ]]))#line:206
            O00OO0000OO0O0O00 .append (OOO00O0O0O0O0000O [OOOO0OO0OOOOOOO00 ])#line:207
    return OOOO000OOO0000000 ,OOOO000O0O0O00O00 ,O00OO0000OO0O0O00 #line:209
def load_common_objects_model (OOO0OOO00OO000OO0 ,O0OOO0O0O00O00000 ):#line:211
    global net #line:212
    try :#line:213
        net =cv2 .dnn .readNet (OOO0OOO00OO000OO0 ,O0OOO0O0O00O00000 )#line:214
        return True #line:215
    except :#line:216
        return False #line:217
class YOLO :#line:220
    def __init__ (O0OOO00OOOO0O00O0 ,OO00OOO0OO00OOO00 ,OO0O0O000O00000OO ,OOO0OO00OOOOO0OO0 ,version ='yolov3'):#line:222
        print ('[INFO] Initializing YOLO ..')#line:224
        O0OOO00OOOO0O00O0 .config =OO0O0O000O00000OO #line:226
        O0OOO00OOOO0O00O0 .weights =OO00OOO0OO00OOO00 #line:227
        O0OOO00OOOO0O00O0 .version =version #line:228
        with open (OOO0OO00OOOOO0OO0 ,'r')as OOOOO00OO00OOOO00 :#line:230
            O0OOO00OOOO0O00O0 .labels =[O0O00OOO000OO00OO .strip ()for O0O00OOO000OO00OO in OOOOO00OO00OOOO00 .readlines ()]#line:231
        O0OOO00OOOO0O00O0 .colors =np .random .uniform (0 ,255 ,size =(len (O0OOO00OOOO0O00O0 .labels ),3 ))#line:233
        O0OOO00OOOO0O00O0 .net =cv2 .dnn .readNet (O0OOO00OOOO0O00O0 .weights ,O0OOO00OOOO0O00O0 .config )#line:235
        OOO0OO0OO0OO00O00 =O0OOO00OOOO0O00O0 .net .getLayerNames ()#line:237
        O0OOO00OOOO0O00O0 .output_layers =[OOO0OO0OO0OO00O00 [O0O0O0OOOO0OOOOOO [0 ]-1 ]for O0O0O0OOOO0OOOOOO in O0OOO00OOOO0O00O0 .net .getUnconnectedOutLayers ()]#line:239
    def detect_objects (OOOO00OOOOOO000O0 ,O00O0OO00OOOOO000 ,confidence =0.5 ,nms_thresh =0.3 ,enable_gpu =False ):#line:243
        if enable_gpu :#line:245
            net .setPreferableBackend (cv2 .dnn .DNN_BACKEND_CUDA )#line:246
            net .setPreferableTarget (cv2 .dnn .DNN_TARGET_CUDA )#line:247
        OOO000O000O0OO0O0 ,O00OOOO0OOO000O0O =O00O0OO00OOOOO000 .shape [:2 ]#line:249
        O0O0O0O0O000O0OO0 =0.00392 #line:250
        OO00O000O00O0O00O =cv2 .dnn .blobFromImage (O00O0OO00OOOOO000 ,O0O0O0O0O000O0OO0 ,(416 ,416 ),(0 ,0 ,0 ),True ,crop =False )#line:253
        OOOO00OOOOOO000O0 .net .setInput (OO00O000O00O0O00O )#line:255
        OO0OOOOO0000OO00O =OOOO00OOOOOO000O0 .net .forward (OOOO00OOOOOO000O0 .output_layers )#line:257
        OO0OO00OO00OOOOOO =[]#line:259
        OOOO0OOO00O000000 =[]#line:260
        O0O00O00O00OOO0OO =[]#line:261
        for O0O0000O000O0OO0O in OO0OOOOO0000OO00O :#line:263
            for O0OO0OOO0O00000O0 in O0O0000O000O0OO0O :#line:264
                O0000O00O0OO0O0OO =O0OO0OOO0O00000O0 [5 :]#line:265
                OOO0OOOO0OO0OO00O =np .argmax (O0000O00O0OO0O0OO )#line:266
                O0O00OO0O00O00O0O =O0000O00O0OO0O0OO [OOO0OOOO0OO0OO00O ]#line:267
                if O0O00OO0O00O00O0O >confidence :#line:268
                    O00O0O0O00OO0OOO0 =int (O0OO0OOO0O00000O0 [0 ]*O00OOOO0OOO000O0O )#line:269
                    O0OOOOO0OO00OO000 =int (O0OO0OOO0O00000O0 [1 ]*OOO000O000O0OO0O0 )#line:270
                    O0OO00O000O0000O0 =int (O0OO0OOO0O00000O0 [2 ]*O00OOOO0OOO000O0O )#line:271
                    O0O0000OO00000O0O =int (O0OO0OOO0O00000O0 [3 ]*OOO000O000O0OO0O0 )#line:272
                    O00O0O0O000O00OOO =O00O0O0O00OO0OOO0 -(O0OO00O000O0000O0 /2 )#line:273
                    O00O0OO000OOO000O =O0OOOOO0OO00OO000 -(O0O0000OO00000O0O /2 )#line:274
                    OO0OO00OO00OOOOOO .append (OOO0OOOO0OO0OO00O )#line:275
                    OOOO0OOO00O000000 .append (float (O0O00OO0O00O00O0O ))#line:276
                    O0O00O00O00OOO0OO .append ([O00O0O0O000O00OOO ,O00O0OO000OOO000O ,O0OO00O000O0000O0 ,O0O0000OO00000O0O ])#line:277
        OOOO0O0O00OO00O0O =cv2 .dnn .NMSBoxes (O0O00O00O00OOO0OO ,OOOO0OOO00O000000 ,confidence ,nms_thresh )#line:280
        OO000O0OOO00OOOOO =[]#line:282
        OO0O000OO0O000OOO =[]#line:283
        O000O00OO000O0000 =[]#line:284
        for OOO000OOO0O000OO0 in OOOO0O0O00OO00O0O :#line:286
            OOO000OOO0O000OO0 =OOO000OOO0O000OO0 [0 ]#line:287
            OO0000000O0OOO0OO =O0O00O00O00OOO0OO [OOO000OOO0O000OO0 ]#line:288
            O00O0O0O000O00OOO =OO0000000O0OOO0OO [0 ]#line:289
            O00O0OO000OOO000O =OO0000000O0OOO0OO [1 ]#line:290
            O0OO00O000O0000O0 =OO0000000O0OOO0OO [2 ]#line:291
            O0O0000OO00000O0O =OO0000000O0OOO0OO [3 ]#line:292
            OO000O0OOO00OOOOO .append ([int (O00O0O0O000O00OOO ),int (O00O0OO000OOO000O ),int (O00O0O0O000O00OOO +O0OO00O000O0000O0 ),int (O00O0OO000OOO000O +O0O0000OO00000O0O )])#line:293
            OO0O000OO0O000OOO .append (str (OOOO00OOOOOO000O0 .labels [OO0OO00OO00OOOOOO [OOO000OOO0O000OO0 ]]))#line:294
            O000O00OO000O0000 .append (OOOO0OOO00O000000 [OOO000OOO0O000OO0 ])#line:295
        return OO000O0OOO00OOOOO ,OO0O000OO0O000OOO ,O000O00OO000O0000 #line:297
    def draw_bbox (O0O0OOOOOO00O00OO ,OOOO00OOO0OO000OO ,O00000OO0O000O0O0 ,OOO0O0O0000O0OOOO ,OOOO0OO00OO0OOO00 ,colors =None ,write_conf =False ):#line:300
        if colors is None :#line:302
            colors =O0O0OOOOOO00O00OO .colors #line:303
        if isinstance (OOO0O0O0000O0OOOO ,list ):#line:305
            for O00OO00O0000OO00O ,O0O0O0OOO0OO000OO in enumerate (OOO0O0O0000O0OOOO ):#line:306
                O000000OO00OOOOOO =colors [O0O0OOOOOO00O00OO .labels .index (O0O0O0OOO0OO000OO )]#line:308
                if write_conf :#line:310
                    O0O0O0OOO0OO000OO +=' '+str (format (OOOO0OO00OO0OOO00 [O00OO00O0000OO00O ]*100 ,'.2f'))+'%'#line:311
                cv2 .rectangle (OOOO00OOO0OO000OO ,(O00000OO0O000O0O0 [O00OO00O0000OO00O ][0 ],O00000OO0O000O0O0 [O00OO00O0000OO00O ][1 ]),(O00000OO0O000O0O0 [O00OO00O0000OO00O ][2 ],O00000OO0O000O0O0 [O00OO00O0000OO00O ][3 ]),O000000OO00OOOOOO ,2 )#line:313
                cv2 .putText (OOOO00OOO0OO000OO ,O0O0O0OOO0OO000OO ,(O00000OO0O000O0O0 [O00OO00O0000OO00O ][0 ],O00000OO0O000O0O0 [O00OO00O0000OO00O ][1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,O000000OO00OOOOOO ,2 )#line:315
        else :#line:316
            O000000OO00OOOOOO =colors [0 ]#line:317
            if write_conf :#line:318
                OOO0O0O0000O0OOOO +=' '+str (format (OOOO0OO00OO0OOO00 *100 ,'.2f'))+'%'#line:319
            cv2 .rectangle (OOOO00OOO0OO000OO ,(O00000OO0O000O0O0 [0 ],O00000OO0O000O0O0 [1 ]),(O00000OO0O000O0O0 [2 ],O00000OO0O000O0O0 [3 ]),O000000OO00OOOOOO ,2 )#line:320
            cv2 .putText (OOOO00OOO0OO000OO ,O0O0O0OOO0OO000OO ,(O00000OO0O000O0O0 [0 ],O00000OO0O000O0O0 [1 ]-10 ),cv2 .FONT_HERSHEY_SIMPLEX ,0.5 ,O000000OO00OOOOOO ,2 )#line:321
class ObjectDetector :#line:324
    _DEFAULT_FOLDER ='c:/roboid/model'#line:325
    def __init__ (O0OOO0OOOO0000OO0 ,multi =False ,lang ='en'):#line:327
        O0OOO0OOOO0000OO0 ._multi =multi #line:328
        O0OOO0OOOO0000OO0 ._lang =lang #line:329
        O0OOO0OOOO0000OO0 ._loaded =False #line:330
        O0OOO0OOOO0000OO0 ._clear ()#line:331
    def _clear (OO0OO00O0OO00OOO0 ):#line:333
        if OO0OO00O0OO00OOO0 ._multi :#line:334
            OO0OO00O0OO00OOO0 ._boxes =[]#line:335
            OO0OO00O0OO00OOO0 ._labels =[]#line:336
            OO0OO00O0OO00OOO0 ._confidences =[]#line:337
        else :#line:338
            OO0OO00O0OO00OOO0 ._boxes =None #line:339
            OO0OO00O0OO00OOO0 ._labels =''#line:340
            OO0OO00O0OO00OOO0 ._confidences =0 #line:341
    def load_model (OOOO0O000OOO000O0 ,folder =None ):#line:343
        try :#line:344
            if folder is None :#line:345
                folder =ObjectDetector ._DEFAULT_FOLDER #line:346
            O00OO0OO000OO00OO =os .path .join (folder ,'object.weights')#line:347
            if os .path .exists (O00OO0OO000OO00OO ):#line:348
                O00000OOOO0OOOO0O =os .path .join (folder ,'object.cfg')#line:349
            else :#line:350
                O00OO0OO000OO00OO =folder +'.weights'#line:351
                O00000OOOO0OOOO0O =folder +'.cfg'#line:352
            if load_common_objects_model (O00OO0OO000OO00OO ,O00000OOOO0OOOO0O ):#line:353
                OOOO0O000OOO000O0 ._loaded =True #line:354
                return True #line:355
            return False #line:356
        except :#line:357
            return False #line:358
    def download_model (O0OOOO0O0O0000O0O ,folder =None ,overwrite =False ):#line:360
        print ('model downloading...')#line:361
        if folder is None :#line:362
            folder =ObjectDetector ._DEFAULT_FOLDER #line:363
        if not os .path .isdir (folder ):#line:364
            os .makedirs (folder )#line:365
        DownloadTool .download_model (folder ,'object.weights',overwrite )#line:366
        DownloadTool .download_model (folder ,'object.cfg',overwrite )#line:367
    def detect (OOOO0O000000OOOO0 ,O00OO0OOO00OOO000 ,conf_threshold =0.5 ,nms_threshold =0.4 ,gpu =False ):#line:369
        if O00OO0OOO00OOO000 is None :#line:370
            OOOO0O000000OOOO0 ._clear ()#line:371
        elif OOOO0O000000OOOO0 ._loaded :#line:372
            OOOO0O0OOO0OOOOOO ,OO00OO00OOOO0O0OO ,OO0O0O000O0OOOO0O =detect_common_objects (O00OO0OOO00OOO000 ,OOOO0O000000OOOO0 ._lang ,conf_threshold ,nms_threshold ,gpu )#line:373
            if OOOO0O000000OOOO0 ._multi :#line:374
                OOOO0O000000OOOO0 ._boxes =OOOO0O0OOO0OOOOOO #line:375
                OOOO0O000000OOOO0 ._labels =OO00OO00OOOO0O0OO #line:376
                OOOO0O000000OOOO0 ._confidences =OO0O0O000O0OOOO0O #line:377
                return len (OO00OO00OOOO0O0OO )>0 #line:378
            else :#line:379
                O00OO0OOOOOOO0O0O =-1 #line:380
                OO0000OO0000OO00O =-1 #line:381
                for O0OO0O0O00O00OOO0 ,OOO0OO00O0OOO000O in enumerate (OOOO0O0OOO0OOOOOO ):#line:382
                    OO0O0000OO0O00O00 =abs (OOO0OO00O0OOO000O [2 ]-OOO0OO00O0OOO000O [0 ])*abs (OOO0OO00O0OOO000O [3 ]-OOO0OO00O0OOO000O [1 ])#line:383
                    if OO0O0000OO0O00O00 >O00OO0OOOOOOO0O0O :#line:384
                        O00OO0OOOOOOO0O0O =OO0O0000OO0O00O00 #line:385
                        OO0000OO0000OO00O =O0OO0O0O00O00OOO0 #line:386
                if OO0000OO0000OO00O <0 :#line:387
                    OOOO0O000000OOOO0 ._boxes =None #line:388
                    OOOO0O000000OOOO0 ._labels =''#line:389
                    OOOO0O000000OOOO0 ._confidences =0 #line:390
                else :#line:391
                    OOOO0O000000OOOO0 ._boxes =OOOO0O0OOO0OOOOOO [OO0000OO0000OO00O ]#line:392
                    OOOO0O000000OOOO0 ._labels =OO00OO00OOOO0O0OO [OO0000OO0000OO00O ]#line:393
                    OOOO0O000000OOOO0 ._confidences =OO0O0O000O0OOOO0O [OO0000OO0000OO00O ]#line:394
                    return True #line:395
        return False #line:396
    def draw_result (OOO0OO0O000O000OO ,OO000O000O0O0OOO0 ,colors =None ,show_conf =False ):#line:398
        if OO000O000O0O0OOO0 is not None :#line:399
            if OOO0OO0O000O000OO ._multi or OOO0OO0O000O000OO ._boxes is not None :#line:400
                OO000O000O0O0OOO0 =draw_bbox (OO000O000O0O0OOO0 ,OOO0OO0O000O000OO ._lang ,OOO0OO0O000O000OO ._boxes ,OOO0OO0O000O000OO ._labels ,OOO0OO0O000O000OO ._confidences ,colors ,show_conf )#line:401
        return OO000O000O0O0OOO0 #line:402
    def get_box (O0OO0OO000OOOOO00 ):#line:404
        return O0OO0OO000OOOOO00 ._boxes #line:405
    def get_label (O0OO0OO00O000O0O0 ):#line:407
        return O0OO0OO00O000O0O0 ._labels #line:408
    def get_conf (O00000OOO000000O0 ):#line:410
        return O00000OOO000000O0 ._confidences #line:411
