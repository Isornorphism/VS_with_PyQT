# -*- coding: utf-8 -*-
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from unit import My, Enemy
from effect import damageEffect
import numpy as np
import math
import config

class myQGraphicsPixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.frameCount = 0
        

class Electromagnetic(QGraphicsPixmapItem):
    def __init__(self, pixmapList, scene, size=128):
        super().__init__()
        self.size = size
        self.level = 1
        self.damage = 5
        self.zlevel = 2
        self.scene = scene
        
        self.setZValue(self.zlevel)
        self.setPos(config.WIN_WIDTH/2, config.WIN_HEIGHT/2)
        #self.setOffset(-self.size/1, -self.size/1+4)

        self.animationIdx = 0
        self.pixmapElectric = pixmapList
        
        self.setOffset(-self.size/2, -self.size/2+4)
        self.setPixmap(self.pixmapElectric[0])
        self.scene.addItem(self)
        
        self.frameCount = 0
        self.attackCoolFrame = 20 # 20프레임마다 공격함, 즉 1/60 * 20 = 1/3 ~ 333ms마다
        
    
    def attack(self):
        if self.frameCount == 0:
            colItem = self.collidingItems()
            for item in colItem:
                if isinstance(item, Enemy) and not item.isDead:
                    item.hp -= self.damage
                    if self.frameCount == 0:
                        self.frameCount += 1
                        
                    if item.hp <= 0:
                        item.isDead = 2
                    item.damageEffectQueue.append(damageEffect(parentItem=item, damage=self.damage,\
                                                              pixmapList=self.scene.sprite.damageNumberList, scene=self.scene))
                    item.hit()
                
        elif self.frameCount > 0:
            self.frameCount += 1
            if self.frameCount >= self.attackCoolFrame:
                self.frameCount = 0

    
    def animationUpdate(self):
        self.animationIdx = self.animationIdx + 1
        if self.animationIdx >= 6:
            self.animationIdx = 0
        self.setPixmap(self.pixmapElectric[self.animationIdx])

    def remove(self):
        self.scene.removeItem(self)
        del self
        


class Bullet(QGraphicsPixmapItem):
    def __init__(self, absPos, dirList, pixmap, size=config.UNIT_SIZE, spd=10.):
        super().__init__()
        self.zlevel = 3
        self.size = size
        
        self.setZValue(self.zlevel)
        
        self.absPos = np.array(absPos)
        self.winPos = np.array([config.WIN_WIDTH/2, config.WIN_HEIGHT/2]) # 초기에는 총알의 위치와 내 위치가 동일
        self.setPos(self.winPos[0], self.winPos[1])
        
        self.setOffset(-self.size/2, -self.size/2)
        self.setPixmap(pixmap)
        
        self.dirList = dirList
        self.spd = spd
        self.isDead = False
        #self.timer.setInterval(300)
           
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
    
    def moveUpdate(self, myAbsPos):
        self.absPos += self.spd * self.dirList
        self.absPos = config.posFilter(self.absPos)
        self.setWinPos(myAbsPos)
        self.setPos(self.winPos[0], self.winPos[1])
            

class Gun():
    def __init__(self, pixmap, scene, spd=10.):
        self.scene = scene
        self.my = [a for a in self.scene.items() if isinstance(a, My)][0]
        self.level = 1
        self.damage = 10
        self.spd = spd
        self.bullet = []
        self.pixmap = pixmap
        self.create_bullet_timer = QTimer(interval=400, timeout=self.createBullet)
        self.create_bullet_timer.start()
        
            
    def bulletUpdate(self, myAbsPos):
        for b in self.bullet:
            b.moveUpdate(myAbsPos)
            colItem = b.collidingItems()
            for item in colItem:
                if isinstance(item, Enemy) and not item.isDead:
                    item.hp -= self.damage
                    if item.hp <= 0:
                        item.isDead = 2
                    item.damageEffectQueue.append(damageEffect(parentItem=item, damage=self.damage,\
                                                          pixmapList=self.scene.sprite.damageNumberList, scene=self.scene))
                    item.hit()
                    b.isDead = True
                    break
        
            if (config.WIN_WIDTH/2 - b.winPos[0])**2 + (config.WIN_HEIGHT/2 - b.winPos[1])**2 > config.GUN_RANGE**2:
                b.isDead = True
            if b.isDead:
                self.bullet.remove(b)
                self.scene.removeItem(b)
                del(b)
            
    
    def createBullet(self):
        if not self.my.isDead:
            if self.scene.prev_dir[2] != self.scene.prev_dir[0] or self.scene.prev_dir[3] != self.scene.prev_dir[1]:
                self.bullet.append(Bullet(self.my.absPos,\
                                          np.array([self.scene.prev_dir[2]-self.scene.prev_dir[0], self.scene.prev_dir[3]-self.scene.prev_dir[1]]),\
                                          pixmap=self.pixmap,\
                                          spd=self.spd))
                self.scene.addItem(self.bullet[-1])
        
    def remove(self):
        for b in self.bullet:
            self.scene.removeItem(b)
            del b
        del self



class Drone():
    def __init__(self, pixmapList, scene, size=64):
        super().__init__()
        self.level = 1
        self.num = 2
        self.damage = 4
        self.zlevel = 2
        self.ang = 0
        self.angVel = 2 # in degree
        self.radi = 150
        self.knockbackRange = 15
        self.attackCoolFrame = 10 # 10프레임마다 공격함, 즉 1/60 * 10 = 1/6 ~ 166ms마다
        
        self.scene = scene
        self.my = [a for a in self.scene.items() if isinstance(a, My)][0]
        
        
        self.animationIdx = 0
        self.pixmapDrone = pixmapList
        self.size = self.pixmapDrone[0].size()
        self.droneItem = []
        
        self.addDrone()
        

    def attack(self):
        for i in range(self.num):
            if self.droneItem[i].frameCount == 0:
                colItem = self.droneItem[i].collidingItems()
                for item in colItem:
                    if isinstance(item, Enemy) and not item.isDead:
                        item.hp -= self.damage
                        if self.droneItem[i].frameCount == 0:
                            self.droneItem[i].frameCount += 1
                            
                        if item.hp <= 0:
                            item.isDead = 2
                        else:
                            theta = math.atan2(item.winPos[1] - config.WIN_HEIGHT/2, item.winPos[0] - config.WIN_WIDTH/2)
                            item.move(self.knockbackRange*np.array([math.cos(theta), math.sin(theta)]), self.my.absPos)
                        item.damageEffectQueue.append(damageEffect(parentItem=item, damage=self.damage,\
                                                                  pixmapList=self.scene.sprite.damageNumberList, scene=self.scene))
                        item.hit()
                    
            elif self.droneItem[i].frameCount > 0:
                self.droneItem[i].frameCount += 1
                if self.droneItem[i].frameCount >= self.attackCoolFrame:
                    self.droneItem[i].frameCount = 0
    
    
    def revoluteDrone(self):
        self.ang += self.angVel
        for i in range(self.num):
            self.droneItem[i].setPos(config.WIN_WIDTH/2 + self.radi*math.cos(i*2*math.pi/self.num + self.ang*math.pi/180),\
                                      config.WIN_HEIGHT/2 + self.radi*math.sin(i*2*math.pi/self.num + self.ang*math.pi/180))
        
    def addDrone(self):
        for i in range(self.num):
            self.droneItem.append(myQGraphicsPixmapItem(self.pixmapDrone[self.animationIdx]))
            self.droneItem[-1].setOffset(-self.size.width()/2, -self.size.height()/2)
            self.droneItem[-1].setPos(config.WIN_WIDTH/2 + self.radi*math.cos(i*2*math.pi/self.num + self.ang*math.pi/180),\
                                      config.WIN_HEIGHT/2 + self.radi*math.sin(i*2*math.pi/self.num + self.ang*math.pi/180))
            self.droneItem[-1].setZValue(self.zlevel)
            
            self.scene.addItem(self.droneItem[-1])
    
    def removeDrone(self):
        for _ in range(self.num):
            self.scene.removeItem(self.droneItem[0])
            del self.droneItem[0]
    
    def remove(self):
        self.removeDrone()
        del self
    
    
    def animationUpdate(self):
        self.animationIdx = self.animationIdx + 1
        if self.animationIdx >= 2:
            self.animationIdx = 0
        for i in range(self.num):
            self.droneItem[i].setPixmap(self.pixmapDrone[self.animationIdx])