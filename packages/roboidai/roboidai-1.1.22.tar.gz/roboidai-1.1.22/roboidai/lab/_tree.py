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


class Node:
    def __init__(self, key):
        self._key = key
        self._left = None
        self._right = None

    def is_terminal(self):
        return self._left is None and self._right is None

    def get_key(self):
        return self._key

    def set_key(self, key):
        self._key = key

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right

    def add_left(self, key):
        node = Node(key)
        self._left = node
        return node

    def add_right(self, key):
        node = Node(key)
        self._right = node
        return node
