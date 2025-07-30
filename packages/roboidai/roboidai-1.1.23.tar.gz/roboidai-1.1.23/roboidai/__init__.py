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

import warnings
warnings.filterwarnings(action='ignore')

from roboidai._camera import Camera
from roboidai._window import Window
from roboidai._keyevent import KeyEvent
from roboidai._image._face_detector import FaceDetector
from roboidai._image._age_gender import AgeGenderDetector
from roboidai._image._expression import FacialExpression
from roboidai._image._object_detector import ObjectDetector
from roboidai._image._face_marker import FaceMarkerDetector
from roboidai._image._face_mesh import FaceMesh
from roboidai._image._hand_pose import HandPose
from roboidai._image._body_pose import BodyPose
from roboidai._image._body_segmentation import BodySegmentation
from roboidai._image._color_detector import ColorDetector
from roboidai._image._aruco_detector import ArucoDetector
from roboidai._image._tool import ImageTool
from roboidai._tm import TmImage
from roboidai._ml import Knn, LinearRegression
from roboidai._navi import SimpleCamRacer, CamRacer
from roboidai import lab
from roboidai import util

__version__ = "1.1.23"

def version():
    import roboid
    import numpy as np
    import tensorflow as tf
    import keras
    import cv2
    print('-' * 20)
    print('roboid:', roboid.__version__)
    print('roboidai:', __version__)
    print('numpy:', np.__version__)
    print('tensorflow:', tf.__version__)
    print('keras:', keras.__version__)
    print('opencv:', cv2.__version__)
    print('-' * 20)

def test_camera(target='all', max_usb=10, max_ip=5, wifi_name=None, user='admin', passwd='admin'):
    Camera.test(target, max_usb, max_ip, wifi_name, user, passwd)

def test_usb_camera(max_usb=10):
    Camera.test('usb', max_usb)

def test_ip_camera(max_ip=5, wifi_name=None, user='admin', passwd='admin'):
    Camera.test('ip', 0, max_ip, wifi_name, user, passwd)
