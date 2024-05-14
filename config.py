# -*- coding: utf-8 -*-
FPS = 60
WIN_WIDTH = 1280
WIN_HEIGHT = 960
MAP_WIDTH = WIN_WIDTH * 5 #6400
MAP_HEIGHT = WIN_HEIGHT * 5 #4800

EMERGE_RADI = 1250
GUN_RANGE = 400
PLAYER_SIZE = 64
UNIT_SIZE = 64
CHUNK_NUM = 5
"""
ELECTRO_PROPERTY = {
        
        }
"""

def posFilter(pos):
    if pos[0] > MAP_WIDTH:
        pos[0] -= MAP_WIDTH
    elif pos[0] < 0:
        pos[0] += MAP_WIDTH
        
    if pos[1] > MAP_HEIGHT:
        pos[1] -= MAP_HEIGHT
    elif pos[1] < 0:
        pos[1] += MAP_HEIGHT
    return pos