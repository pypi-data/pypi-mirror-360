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

import roboidai.lab._image as _image
import roboidai.lab._fruit_detector as _fruit_detector
import roboidai.lab._line_recorder as _line_recorder
import roboidai.lab._q_world as _q_world
from roboidai.lab._q_world import QWorld
import roboidai.lab._zoo as _zoo
import roboidai.lab._track as _track
from roboidai.lab._tree import Node


_LANG = 'ko'

def collect_image(cam, folder):
    _image.collect_image(cam, folder, _LANG)

def record_image(cam, folder, interval_msec=100, frames=20, countdown=3):
    _image.record_image(cam, folder, interval_msec, frames, countdown, _LANG)

def collect_color(cam, labels, color_space='hsv'):
    return _image.collect_color(cam, labels, color_space, _LANG)

def capture_color(cam, color_space='hsv'):
    return _image.capture_color(cam, color_space, _LANG)

def wait_until_fruit(cam, fruits, interval_msec=1):
    return _fruit_detector.wait_until_fruit(cam, fruits, interval_msec, _LANG)

def record_hamster(file_path):
    _line_recorder.record_hamster(file_path, _LANG)

def record_hamster_s(file_path):
    _line_recorder.record_hamster_s(file_path, _LANG)

def record_driving(robot, file_path):
    _line_recorder.record_driving(robot, file_path, _LANG)

def play_q_game_hamster():
    _q_world.play_q_game_hamster()

def play_q_game_hamster_s(cross=True):
    _q_world.play_q_game_hamster_s(cross)

def move_zoo(robot, animal):
    _zoo.move_zoo(robot, animal, _LANG)

def play_zoo_cam(robot, cam, model_folder=None):
    _zoo.play_zoo_cam(robot, cam, model_folder, _LANG)

def play_zoo_tree(robot):
    _zoo.play_zoo_tree(robot, _LANG)

def find_track_xy(image, output, color, h_range, s_range=(50,255), v_range=(50,255), window_height=-1, min_area=0):
    return _track.find_track_xy(image, output, color, h_range, s_range, v_range, window_height, min_area)

def find_green_track_xy(image, output, h_range=(40, 80), s_range=(50,255), v_range=(50,255), window_height=-1, min_area=0):
    return _track.find_green_track_xy(image, output, h_range, s_range, v_range, window_height, min_area)

def find_blue_track_xy(image, output, h_range=(100, 140), s_range=(50,255), v_range=(50,255), window_height=-1, min_area=0):
    return _track.find_blue_track_xy(image, output, h_range, s_range, v_range, window_height, min_area)

def find_red_track_xy(image, output, h_range=(0, 10, 170, 180), s_range=(50,255), v_range=(50,255), window_height=-1, min_area=0):
    return _track.find_red_track_xy(image, output, h_range, s_range, v_range, window_height, min_area)
