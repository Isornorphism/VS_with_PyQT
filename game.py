# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QRectF, QSize, QTimer, QPointF, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItemGroup
import config
from unit import Enemy, My
from skill import Electromagnetic, Bullet, Gun, Drone
from effect import damageEffect
from ui import scoreBoard, globalTimerBoard, Bar, chooseSkillWindow, pauseWindow
from sprite import Sprite
import random
import numpy as np
import math
#import gc, psutil, tracemalloc


class myScene(QGraphicsScene):
    pauseSig = pyqtSignal()
    levelupSig = pyqtSignal()
    #afterChooseSkillSig = pyqtSignal()
    
    def __init__(self, qrectf):
        super().__init__(qrectf)
        self.dir = [0 for _ in range(4)]
        self.prev_dir = [0, 0, 0, 1]
        self.isPause = False
        
        self.keyInputMode = "game"
        
        self.sprite = Sprite()
        
        self.backgroundImg = QPixmap("./img/background_tile.png")
        self.bg_item = QGraphicsRectItem()
        self.bg_item.setRect(-2*self.backgroundImg.width(), -2*self.backgroundImg.height(),\
                             config.WIN_WIDTH + 4*self.backgroundImg.width(), config.WIN_HEIGHT + 4*self.backgroundImg.height())
        self.bg_item.setBrush(QBrush(self.backgroundImg))
        self.bg_item.setPen(QPen(0))
        self.bg_item.setZValue(-1)
        self.addItem(self.bg_item)
        
        self.e = []
        self.my = My(self)
    
        self.scoreBoard = scoreBoard([config.WIN_WIDTH, 0], alignMode = "right", pixmapList=self.sprite.scoreNumberList, scene=self)
        self.globalTimerBoard = globalTimerBoard([config.WIN_WIDTH/2, 0], pixmapList=self.sprite.timeNumberList,\
                                                 pixmapColon=self.sprite.timeColon, scene=self)
        self.score = 0
        self.hpBar = Bar(winPos=[20, 20], pixmap=self.sprite.hpBarSprite, maxPixel=204, height=16, startX=6, startY=22,\
                         barColor=QColor(233, 35, 70), compBarColor=QColor(138, 2, 64), pixmapNumberList=self.sprite.hpNumberList,\
                         initGauge=self.my.hp, initMaxGauge=self.my.maxHP, scene=self)
        
        self.expBar = Bar(winPos=[20, 80], pixmap=self.sprite.expBarSprite, maxPixel=204, height=8, startX=6, startY=22,\
                          barColor=QColor(27, 183, 250), compBarColor=QColor(91,102, 159), pixmapNumberList=self.sprite.expNumberList,\
                          initGauge=self.my.exp, initMaxGauge=self.my.maxEXP, scene=self)
        
        self.cnt = 0
        
        self.electro = Electromagnetic(self.sprite.electromagneticList, self)
        self.gun = Gun(self.sprite.bulletSprite, self)
        self.drone = Drone(self.sprite.droneList, self)
        
        self.pauseSig.connect(self.createPauseWindow)
        self.levelupSig.connect(self.createChooseSkillWindow)
        #self.afterChooseSkillSig.connect(self.removeChooseSkillWindow)
              
        self._interval = 1000 / config.FPS
        self.base_timer = QTimer(self, interval=self._interval, timeout = self.base_timeout)
        self.animation_timer = QTimer(self, interval=self._interval*6, timeout = self.animation_timeout)
        #self.global_timer = QTimer(self, interval=1000, timeout = self.global_timeout)
        self.base_timer.start()
        self.animation_timer.start()
        #self.global_timer.start()
        
        
        
    def createEnemy(self):
        r = random.randint(0, 100)
        if r < 3:
            ang = random.randint(0, 360)
            e_pos = config.posFilter(config.EMERGE_RADI * np.array([math.cos(ang * math.pi/180), math.sin(ang * math.pi/180)])+self.my.absPos)
            self.e.append(Enemy(e_pos, self.my.absPos,\
                                self.sprite.zombieRightMoveList, self.sprite.zombieLeftMoveList,\
                                self.sprite.zombieFrontMoveList, self.sprite.zombieBackMoveList,\
                                self.sprite.zombieDamageRightMoveList, self.sprite.zombieDamageLeftMoveList,\
                                self.sprite.zombieDamageFrontMoveList, self.sprite.zombieDamageBackMoveList, self.sprite.zombieDeathList, self))
    
    
    def moveBackground(self, my_spd):
        bg_x = self.bg_item.x() - my_spd*(self.dir[2]-self.dir[0])
        bg_y = self.bg_item.y() - my_spd*(self.dir[3]-self.dir[1])
        
        if bg_x < -2*self.backgroundImg.width():
            bg_x += self.backgroundImg.width()
        elif bg_x > 0:
            bg_x -= self.backgroundImg.width()
            
        if bg_y < -2*self.backgroundImg.height():
            bg_y += self.backgroundImg.height()
        elif bg_y > 0:
            bg_y -= self.backgroundImg.height()        
            
        self.bg_item.setPos(bg_x, bg_y)
    
    
        
    def base_timeout(self):
        
        # 모든 객체 이동
        if not self.my.isDead:
            self.my.moveUpdate()
            self.moveBackground(self.my.spd)
            
            self.gun.bulletUpdate(self.my.absPos)
            self.drone.revoluteDrone()

        for e in self.e:
            if e.isInChunk(self.my.chunkMtx):
                if not e.isDead:
                    e.moveUpdate(self.my.absPos)
                else:
                    e.setWinPos(self.my.absPos)
                    e.setPos(e.winPos[0], e.winPos[1])
        
        # 모든 객체 피격 판정
        isHPChanged = False
        if not self.my.isDead:
            isHPChanged = self.my.damage()
            self.electro.attack()
            self.drone.attack()
        
        # 객체 사망 여부 판정
        if self.my.isDead == 2:
            self.my.isDead = 1
            self.electro.remove()
            self.gun.remove()
            self.drone.remove()
            self.my.animationIdx = 0
        
        isScoreChanged = False
        for e in self.e:
            if e.isDead == 2: # now dead -> only one time score, exp up
                e.isDead = 1
                e.animationIdx = 0
                isScoreChanged = True
                self.score += e.score
                self.my.exp += e.exp
                self.my.checkLevelUp()
                
                
                #self.e.remove(e)
                #e.remove()
        
        # ui 갱신
        if isHPChanged:
            self.hpBar.setGauge(self.my.hp, self.my.maxHP)
        if isScoreChanged:
            self.expBar.setGauge(self.my.exp, self.my.maxEXP)
            self.scoreBoard.setScore(self.score)
        #if isLevelChanged:
            #self.levelupSig.emit()
        
        # 적 생성
        self.createEnemy()
        
        
        #found_objs = gc.get_objects()
        #print(len(found_objs))
        #t2 = tracemalloc.take_snapshot()
        #stats = t2.compare_to(t1, 'traceback')
        #top = stats[:3]
        #print("\n".join(top.traceback.format()))
        #for stat in stats[:3]:
        #    print(stat.traceback.format())
        #print()
        
        #else:
        #    self.animation_timer.stop()
    
    
    def animation_timeout(self):
        if not self.my.isDead:
            self.my.animationUpdate()
            self.electro.animationUpdate()
            self.drone.animationUpdate()
        elif self.my.isDead == 1:
            if self.my.animationIdx == 18: # 클수록 오래 기다림
                self.pauseSig.emit()
            else:
                self.my.deathAnimation()
                
        
        for e in self.e:
            if e.isInChunk(self.my.chunkMtx):
                if not e.isDead:
                    e.animationUpdate()
                elif e.isDead == 1:
                    if e.animationIdx == 6:
                        self.e.remove(e)
                        e.remove()
                    else:
                        e.deathAnimation()
            
        print("Abs position : ", self.my.absPos, "\t Chunk : ", self.my.chunkMtx)
        print("Total enemy : ", len(self.e), "\t Active enemy : ", len([e for e in self.e if e.isInChunk(self.my.chunkMtx)]))
        print("My level : ", self.my.level)
        print()
    
    
    def pauseGame(self):
        if not self.isPause:
            self.base_timer.stop()
            self.animation_timer.stop()
            self.globalTimerBoard.global_timer.stop()
            self.gun.create_bullet_timer.stop()
            self.isPause = True
        else:
            self.base_timer.start()
            self.animation_timer.start()
            self.globalTimerBoard.global_timer.start()
            self.gun.create_bullet_timer.start()
            self.isPause = False
        
        
    def createChooseSkillWindow(self):
        self.pauseGame()
        self.chooseSkillWindow = chooseSkillWindow(skillList=["전자기장", "강철 심장", "AK-47", "드론"], scene=self)
        self.keyInputMode = "selectSkill"
    
    def removeChooseSkillWindow(self):
        self.pauseGame()
        self.chooseSkillWindow.remove()
        self.keyInputMode = "game"
        
        
    def createPauseWindow(self):
        self.pauseGame()
        self.pauseWindow = pauseWindow(scene=self)
        self.keyInputMode = "pause"
    
    def removePauseWindow(self):
        self.pauseGame()
        self.pauseWindow.remove()
        self.keyInputMode = "game"




class Game(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(config.WIN_WIDTH, config.WIN_HEIGHT)) # 사이즈 고정
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scene = myScene(QRectF(0, 0, config.WIN_WIDTH, config.WIN_HEIGHT))
        self.setScene(self.scene)
        
        
    def keyPressEvent(self, e):
        if self.scene.keyInputMode == "game":
            if e.key() == Qt.Key_Left:
                self.scene.dir[0] = 1
            if e.key() == Qt.Key_Up:
                self.scene.dir[1] = 1
            if e.key() == Qt.Key_Right:
                self.scene.dir[2] = 1
            if e.key() == Qt.Key_Down:
                self.scene.dir[3] = 1
            if e.key() == Qt.Key_Escape:
                self.scene.pauseSig.emit()
                
            self.scene.prev_dir = self.scene.dir.copy() # shallow copy
        
        elif self.scene.keyInputMode == "selectSkill":
            prevNum = self.scene.chooseSkillWindow.selectedSkillNum
            if e.key() == Qt.Key_Left:
                self.scene.chooseSkillWindow.selectedSkillNum = (self.scene.chooseSkillWindow.selectedSkillNum+2)%3
            if e.key() == Qt.Key_Right:
                self.scene.chooseSkillWindow.selectedSkillNum = (self.scene.chooseSkillWindow.selectedSkillNum+1)%3
            
            if prevNum != self.scene.chooseSkillWindow.selectedSkillNum:
                self.scene.chooseSkillWindow.candidateItem[prevNum].childItems()[0].setPen(QPen(Qt.black, 1))
                self.scene.chooseSkillWindow.candidateItem[self.scene.chooseSkillWindow.selectedSkillNum].childItems()[0].setPen(QPen(Qt.black, 3))
                
            
            if e.key() == Qt.Key_R: #reroll
                if self.scene.chooseSkillWindow.rerollNum:
                    self.scene.chooseSkillWindow.candidateList = self.scene.chooseSkillWindow.selectRandomSkill(self.scene.chooseSkillWindow.skillList)
                    for i in range(3):
                        self.scene.chooseSkillWindow.candidateItem[i].childItems()[1].setPlainText(self.scene.chooseSkillWindow.candidateList[i])
                        self.scene.chooseSkillWindow.candidateItem[i].childItems()[1].setPos(config.WIN_WIDTH/2\
                                          -self.scene.chooseSkillWindow.candidateItem[i].childItems()[1].boundingRect().width()/2+(i-1)*300, 300)
                    self.scene.chooseSkillWindow.rerollNum -= 1
            
            if e.key() == Qt.Key_Space: #select
                # TBD
                if self.scene.chooseSkillWindow.candidateList[self.scene.chooseSkillWindow.selectedSkillNum] == "강철 심장":
                    self.scene.my.maxHP += 10
                    self.scene.my.hp += 10
                    self.scene.hpBar.setGauge(self.scene.my.hp, self.scene.my.maxHP)
                
                elif self.scene.chooseSkillWindow.candidateList[self.scene.chooseSkillWindow.selectedSkillNum] == "드론":
                    self.scene.drone.removeDrone()
                    self.scene.drone.num += 1
                    self.scene.drone.addDrone()
                #self.scene.afterChooseSkillSig.emit()
                self.scene.removeChooseSkillWindow()
        
        elif self.scene.keyInputMode == "pause":
            if e.key() == Qt.Key_R:
                del self.scene
                self.scene = myScene(QRectF(0, 0, config.WIN_WIDTH, config.WIN_HEIGHT))
                self.setScene(self.scene)
            
            elif e.key() == Qt.Key_Escape:
                self.scene.removePauseWindow()
            
        
            
    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.scene.dir[0] = 0
        if e.key() == Qt.Key_Up:
            self.scene.dir[1] = 0
        if e.key() == Qt.Key_Right:
            self.scene.dir[2] = 0
        if e.key() == Qt.Key_Down:
            self.scene.dir[3] = 0
            
        if sum(self.scene.dir) != 0:
            self.scene.prev_dir = self.scene.dir.copy() # shallow copy
        
        