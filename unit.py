# -*- coding: utf-8 -*-
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsColorizeEffect
import math
import numpy as np
import random
from collections import deque
import config


class Enemy(QGraphicsPixmapItem):
    def __init__(self, absPos, myAbsPos, pixmapRightMoveList, pixmapLeftMoveList, pixmapFrontMoveList, pixmapBackMoveList,\
                 pixmapDamageRightMoveList, pixmapDamageLeftMoveList, pixmapDamageFrontMoveList, pixmapDamageBackMoveList, pixmapDeathList, scene, size=config.UNIT_SIZE, spd=2.):
        super().__init__()
        self.scene = scene
        self.size = size
        self.zlevel = 3
        self.setZValue(self.zlevel)
        
        self.absPos = np.array(absPos)
        self.winPos = np.array([0, 0])
        self.chunkMtx = np.array([0, 0])
        self.setChunk()
        self.setWinPos(myAbsPos)
        self.setPos(self.winPos[0], self.winPos[1])
        
        self.dirAngle = 0
        self.animationIdx = 0
        self.pixmapFrontMoveList = pixmapFrontMoveList
        self.pixmapBackMoveList = pixmapBackMoveList
        self.pixmapRightMoveList = pixmapRightMoveList
        self.pixmapLeftMoveList = pixmapLeftMoveList
        self.pixmapDamageFrontMoveList = pixmapDamageFrontMoveList
        self.pixmapDamageBackMoveList = pixmapDamageBackMoveList
        self.pixmapDamageRightMoveList = pixmapDamageRightMoveList
        self.pixmapDamageLeftMoveList = pixmapDamageLeftMoveList
        self.pixmapDeathList = pixmapDeathList
        
        self.setOffset(-self.size/2, -self.size/2)
        self.setPixmap(self.pixmapFrontMoveList[0])
        self.scene.addItem(self)
        
        self.isDead = 0 # 0 : not dead, 1 : dead(ing), 2 : now dead
        self.isHit = False
        self.hp = 40
        self.exp = 5
        self.damage = 5
        self.spd = spd
        self.score = 5
        
        self.damageEffectQueue = deque()
        self.hit_timer = QTimer(interval=300, timeout = self.hit_timeout)
        
    """
    def paint(self, qp, opt, widget):
        super().paint(qp, opt, widget)
        font = QFont("arial", 10)
        qp.setFont(font)
        qp.drawText(self.boundingRect(), Qt.AlignCenter, str(self.hp))
    """    
    
    def move(self, deltaPos, myAbsPos):
        self.absPos += deltaPos
        self.absPos = config.posFilter(self.absPos)        
        self.setChunk()
        self.setWinPos(myAbsPos)
        
    def moveUpdate(self, myAbsPos):
        self.dirAngle = math.atan2(config.WIN_HEIGHT/2 - self.winPos[1], config.WIN_WIDTH/2 - self.winPos[0])
        randAngle = random.randint(0, 180)*math.pi/180
        randRange = random.gauss(0, 1)
        self.move(self.spd * np.array([math.cos(self.dirAngle), math.sin(self.dirAngle)]) + randRange * np.array([math.cos(randAngle), math.sin(randAngle)]),\
                  myAbsPos)
        
        if self.isInWindow():
            self.setPos(self.winPos[0], self.winPos[1])
            self.setVisible(True)
        else:
            self.setVisible(False)
            
            
    def animationUpdate(self):
        self.animationIdx = self.animationIdx + 1
        #print(self.dirAngle)
        if self.animationIdx >= 6:
            self.animationIdx = 0
            
        if not self.isHit:
            if self.dirAngle >= -math.pi/4 and self.dirAngle < math.pi/4: # right
                self.setPixmap(self.pixmapRightMoveList[self.animationIdx])
            elif self.dirAngle >= -3*math.pi/4 and self.dirAngle < -math.pi/4: # back
                self.setPixmap(self.pixmapBackMoveList[self.animationIdx])
            elif self.dirAngle >= math.pi/4 and self.dirAngle < 3*math.pi/4: # front
                self.setPixmap(self.pixmapFrontMoveList[self.animationIdx])
            else: # left
                self.setPixmap(self.pixmapLeftMoveList[self.animationIdx])
        else:
            if self.dirAngle >= -math.pi/4 and self.dirAngle < math.pi/4: # right
                self.setPixmap(self.pixmapDamageRightMoveList[self.animationIdx])
            elif self.dirAngle >= -3*math.pi/4 and self.dirAngle < -math.pi/4: # back
                self.setPixmap(self.pixmapDamageBackMoveList[self.animationIdx])
            elif self.dirAngle >= math.pi/4 and self.dirAngle < 3*math.pi/4: # front
                self.setPixmap(self.pixmapDamageFrontMoveList[self.animationIdx])
            else: # left
                self.setPixmap(self.pixmapDamageLeftMoveList[self.animationIdx])
        
    def deathAnimation(self):
        self.setPixmap(self.pixmapDeathList[self.animationIdx])
        self.animationIdx += 1
        print(self.animationIdx)
    
    def setChunk(self):
        self.chunkMtx[0] = self.absPos[0]//config.WIN_WIDTH
        self.chunkMtx[1] = self.absPos[1]//config.WIN_HEIGHT
    
    
    def isInWindow(self):
        return abs(self.winPos[0] - config.WIN_WIDTH/2) < config.WIN_WIDTH + self.size and\
               abs(self.winPos[1] - config.WIN_HEIGHT/2) < config.WIN_HEIGHT + self.size
    
    def isInChunk(self, myChunkMtx):
        if myChunkMtx[0] == 0:
            xCheck = self.chunkMtx[0] in [0, 1, config.CHUNK_NUM-1]
        elif myChunkMtx[0] == config.CHUNK_NUM - 1:
            xCheck = self.chunkMtx[0] in [0, config.CHUNK_NUM-2, config.CHUNK_NUM-1]
        else:
            xCheck = self.chunkMtx[0] in [myChunkMtx[0]-1, myChunkMtx[0], myChunkMtx[0]+1]
        
        if myChunkMtx[1] == 0:
            yCheck = self.chunkMtx[1] in [0, 1, config.CHUNK_NUM-1]
        elif myChunkMtx[1] == config.CHUNK_NUM - 1:
            yCheck = self.chunkMtx[1] in [0, config.CHUNK_NUM-2, config.CHUNK_NUM-1]
        else:
            yCheck = self.chunkMtx[1] in [myChunkMtx[1]-1, myChunkMtx[1], myChunkMtx[1]+1]
        
        return xCheck and yCheck


    # My 위치를 [config.WIN_WIDTH/2, config.WIN_HEIGHT/2]로 둘 때 enemy의 상대 좌표
    def setWinPos(self, myAbsPos):
        self.winPos[0] = self.absPos[0] - myAbsPos[0] + config.WIN_WIDTH/2
        self.winPos[1] = self.absPos[1] - myAbsPos[1] + config.WIN_HEIGHT/2
        
        if self.absPos[0] - myAbsPos[0] < -config.MAP_WIDTH/2:
            self.winPos[0] += config.MAP_WIDTH
        elif self.absPos[0] - myAbsPos[0] > config.MAP_WIDTH/2:
            self.winPos[0] -= config.MAP_WIDTH
        
        if self.absPos[1] - myAbsPos[1] < -config.MAP_HEIGHT/2:
            self.winPos[1] += config.MAP_HEIGHT
        elif self.absPos[1] - myAbsPos[1] > config.MAP_HEIGHT/2:
            self.winPos[1] -= config.MAP_HEIGHT
    
    def hit(self):
        self.isHit = True
        self.hit_timer.start()
    
    def hit_timeout(self):
        self.isHit = False
        self.hit_timer.stop()
    
    
    def removeEffect(self):
        self.damageEffectQueue.popleft()
    
    def remove(self):
        for eff in self.damageEffectQueue:
            #eff.setInvisible()
            eff.remove()
        self.scene.removeItem(self)
        del self
    
    
    
    
class My(QGraphicsPixmapItem):
    def __init__(self, scene, size=config.UNIT_SIZE, spd=5.):
        super().__init__()
        self.setFlag(self.ItemIsFocusable)
        self.setFocus()
        
        self.zlevel = 5
        self.setZValue(self.zlevel)
        self.scene = scene
        
        self.absPos = np.array([config.MAP_WIDTH/2, config.MAP_HEIGHT/2])
        #winPos is always [win_width/2, win_height/2]
        self.chunkMtx = np.array([config.CHUNK_NUM//2, config.CHUNK_NUM//2]) #default : [2, 2]
        self.setPos(config.WIN_WIDTH/2, config.WIN_HEIGHT/2)
        
        self.animationNum = 6
        self.animationIdx = 0
        self.pixmapFrontMoveList = [QPixmap("./img/my/front_move_" + str(i+1) + ".png") for i in range(self.animationNum)]
        self.pixmapBackMoveList = [QPixmap("./img/my/back_move_" + str(i+1) + ".png") for i in range(self.animationNum)]
        self.pixmapRightMoveList = [QPixmap("./img/my/beside_move_" + str(i+1) + ".png") for i in range(self.animationNum)]
        self.pixmapFrontIdleList = [QPixmap("./img/my/front_idle_" + str(i+1) + ".png") for i in range(self.animationNum//3)]
        self.pixmapBackIdleList = [QPixmap("./img/my/back_idle_" + str(i+1) + ".png") for i in range(self.animationNum//3)]
        self.pixmapRightIdleList = [QPixmap("./img/my/beside_idle_" + str(i+1) + ".png") for i in range(self.animationNum//3)]
        self.pixmapInfList = [QPixmap("./img/my/death_inf_" + str(i+1) + ".png") for i in range(self.animationNum)]
        
        self.pixmapLeftMoveList = [pm.transformed(QTransform().scale(-1, 1)) for pm in self.pixmapRightMoveList]
        self.pixmapLeftIdleList = [pm.transformed(QTransform().scale(-1, 1)) for pm in self.pixmapRightIdleList]
        
        self.size = size
        self.setOffset(-self.size/2, -self.size/2)
        self.setPixmap(self.pixmapFrontMoveList[0])
        self.scene.addItem(self)
        
        self.isDead = 0 # 0 : not dead, 1 : dead(ing), 2 : now dead
        
        self.spd = spd
        self.maxHP = 20
        self.hp = 20
        self.level = 1
        self.maxEXP = 50
        self.exp = 0
        
        self.frameCount = 0
        self.damageCoolFrame = 60 # 60프레임마다 피격당함, 즉 1/60 * 60 = 1s마다
        
        
    
    def focusOutEvent(self, e):
        self.setFocus()

  
    def moveUpdate(self, spd=5.0):
        if self.scene.dir[0]:
            self.absPos[0] -= self.spd
        if self.scene.dir[1]:
            self.absPos[1] -= self.spd
        if self.scene.dir[2]:
            self.absPos[0] += self.spd
        if self.scene.dir[3]:
            self.absPos[1] += self.spd
        
        self.absPos = config.posFilter(self.absPos)
        self.setChunk()
            
            
    def animationUpdate(self):
        self.animationIdx += 1
        if self.animationIdx >= self.animationNum:
            self.animationIdx = 0
        
        if sum(self.scene.dir) != 0: #move
            if self.scene.dir[2]-self.scene.dir[0]>0: # right
                self.setPixmap(self.pixmapRightMoveList[self.animationIdx])
            elif self.scene.dir[2]-self.scene.dir[0]<0: #left
                self.setPixmap(self.pixmapLeftMoveList[self.animationIdx])
            else: #front or back
                if self.scene.dir[3]-self.scene.dir[1]>0: #front
                    self.setPixmap(self.pixmapFrontMoveList[self.animationIdx])
                else: #back
                    self.setPixmap(self.pixmapBackMoveList[self.animationIdx])
        
        else: #idle
            if self.scene.prev_dir[2]-self.scene.prev_dir[0]>0: # right
                self.setPixmap(self.pixmapRightIdleList[self.animationIdx//3])
            elif self.scene.prev_dir[2]-self.scene.prev_dir[0]<0: #left
                self.setPixmap(self.pixmapLeftIdleList[self.animationIdx//3])
            else: #front or back
                if self.scene.prev_dir[3]-self.scene.prev_dir[1]>0: #front
                    self.setPixmap(self.pixmapFrontIdleList[self.animationIdx//3])
                else: #back
                    self.setPixmap(self.pixmapBackIdleList[self.animationIdx//3])
                    
    def deathAnimation(self):
        self.setPixmap(self.pixmapInfList[min(self.animationIdx, 5)])
        self.animationIdx += 1
                    
    def setChunk(self):
        self.chunkMtx[0] = self.absPos[0]//config.WIN_WIDTH
        self.chunkMtx[1] = self.absPos[1]//config.WIN_HEIGHT
       
        
    def checkLevelUp(self):
        if self.exp >= self.maxEXP:
            self.exp -= self.maxEXP
            self.level += 1
            self.scene.levelupSig.emit()


    def damage(self):
        if self.frameCount == 0:
            colItem = self.collidingItems()
            for item in colItem:
                if isinstance(item, Enemy) and not item.isDead:
                    self.hp = max(self.hp-item.damage, 0)
                    if self.hp == 0:
                        self.isDead = 2
                    self.frameCount += 1
                    return True
                
        elif self.frameCount > 0:
            self.frameCount += 1
            if self.frameCount >= self.damageCoolFrame:
                self.frameCount = 0
        
        return False
             
                   