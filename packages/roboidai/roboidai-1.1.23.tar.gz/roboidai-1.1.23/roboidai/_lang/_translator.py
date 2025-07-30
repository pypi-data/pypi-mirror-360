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


_TEXTS = {
    'en': {
        'lab._image.capture_color': 'Press SPACE key to collect color data or ESC key to quit.',
        'lab._image.capture_image': 'Press SPACE key to save image or ESC key to quit.',
        'lab._image.record_image': 'Press ESC key to quit.',
        'lab._image.saved': 'saved',
        'lab._line_tracer.usage': 'Press space key to start a robot.\nIt stops automatically when arrived.\nPress ESC key to save data and quit.\n',
        'lab._line_tracer.saved': 'Saved to {}'
    },
    'ko': {
        'lab._image.capture_color': '스페이스 키를 누르면 색깔 데이터를 수집하고 ESC 키를 누르면 종료합니다.',
        'lab._image.capture_image': '스페이스 키를 누르면 영상 한 장을 저장하고 ESC 키를 누르면 종료합니다.',
        'lab._image.record_image': 'ESC 키를 누르면 종료합니다.',
        'lab._image.saved': '저장됨',
        'lab._line_tracer.usage': '스페이스 키를 누르면 로봇이 출발합니다.\n도착하면 자동으로 정지합니다.\nESC 키를 누르면 데이터를 저장하고 종료합니다.\n',
        'lab._line_tracer.saved': '{}에 저장되었습니다.'
    }
}

def translate(key, lang='en'):
    texts = _TEXTS[lang] if lang in _TEXTS else _TEXTS['en']
    return texts[key] if key in texts else ''
