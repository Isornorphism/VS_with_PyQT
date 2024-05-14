# -*- coding: utf-8 -*-
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItemGroup
import numpy as np
import math
import random
import config


class scoreBoard():
    def __init__(self, winPos, alignMode, pixmapList, scene):
        self.alignMode = alignMode
        self.digit = 8
        self.winPos = winPos
        self.scene = scene
        self.numberList = []
        
        self.pixmapList = pixmapList
        self.size = self.pixmapList[0].size()
        self.setScore(0)
        
    
    def setScore(self, score):
        for n in self.numberList:
            self.scene.removeItem(n)
            del(n)
        self.numberList.clear()
        
        tmp = score
        if tmp == 0:
            for _ in range(self.digit):
                self.numberList.append(self.pixmapList[0])
        else:
            cnt = 0
            while tmp != 0:
                self.numberList.append(self.pixmapList[tmp % 10])
                tmp = tmp // 10
                cnt += 1
            for _ in range(self.digit - cnt):
                self.numberList.append(self.pixmapList[0])
        
        if self.alignMode == "left":
            self.numberList.reverse()
            for i in range(self.digit):
                self.numberList[i] = QGraphicsPixmapItem(self.numberList[i])
                self.numberList[i].setPos(self.winPos[0] + i*self.size.width(), self.winPos[1])
                self.numberList[i].setZValue(10)
                self.scene.addItem(self.numberList[i])
                #self.(pixmapItem)
            
        elif self.alignMode == "right":
            for i in range(self.digit):
                self.numberList[i] = QGraphicsPixmapItem(self.numberList[i])
                self.numberList[i].setPos(self.winPos[0] -(i+1)*self.size.width(), self.winPos[1])
                self.numberList[i].setZValue(10)
                self.scene.addItem(self.numberList[i])
                #self.addToGroup(pixmapItem)


class globalTimerBoard():
    def __init__(self, winPos, pixmapList, pixmapColon, scene):
        self.sec = 0
        self.winPos = winPos
        self.scene = scene
        self.secList = []
        self.minList = []
        
        self.pixmapList = pixmapList
        self.size = self.pixmapList[0].size()
        
        self.pixmapColon = QGraphicsPixmapItem(pixmapColon)
        self.pixmapColon.setPos(self.winPos[0] - self.size.width()/2, self.winPos[1])
        self.pixmapColon.setZValue(10)
        self.scene.addItem(self.pixmapColon)
        self.setTime()
        
        
        self.global_timer = QTimer(interval=1000, timeout = self.setTime)
        self.global_timer.start()
        
    
    def setTime(self):
        for s in self.secList:
            self.scene.removeItem(s)
            del(s)
        self.secList.clear()
        for m in self.minList:
            self.scene.removeItem(m)
            del(m)
        self.minList.clear()
        
        minute = self.sec // 60
        second = self.sec % 60
        
        self.minList = self.getDigit(minute)
        self.secList = self.getDigit(second)
        #print(self.minList, self.secList)
    
        for i in range(2):
            self.minList[i] = QGraphicsPixmapItem(self.minList[i])
            self.minList[i].setPos(self.winPos[0] - (i+3/2)*self.size.width(), self.winPos[1])
            self.minList[i].setZValue(10)
            self.scene.addItem(self.minList[i])
        
        self.secList.reverse()
        for i in range(2):
            self.secList[i] = QGraphicsPixmapItem(self.secList[i])
            self.secList[i].setPos(self.winPos[0] + (i+1/2)*self.size.width(), self.winPos[1])
            self.secList[i].setZValue(10)
            self.scene.addItem(self.secList[i])
        
        self.sec += 1
        
        
    def getDigit(self, num):
        tmp = num
        numList = []
        if tmp == 0:
            for _ in range(2):
                numList.append(self.pixmapList[0])
        else:
            digit = 0
            while tmp != 0:
                numList.append(self.pixmapList[tmp % 10])
                tmp = tmp // 10
                digit += 1
                
            for _ in range(2 - digit):
                numList.append(self.pixmapList[0])
        return numList



class Bar():
    def __init__(self, winPos, pixmap, maxPixel, height, startX, startY, barColor, compBarColor, pixmapNumberList, initGauge, initMaxGauge, scene):
        self.winPos = winPos
        self.scene = scene
        
        self.pixmap = pixmap
        self.size = self.pixmap.size()
        
        self.barFrame = QGraphicsPixmapItem(pixmap)
        self.barFrame.setPos(self.winPos[0], self.winPos[1])
        self.barFrame.setZValue(11)
        self.scene.addItem(self.barFrame)
        
        self.maxPixel = maxPixel
        
        self.compBar = QGraphicsRectItem(startX, startY, self.maxPixel, height, parent=self.barFrame)
        self.compBar.setFlag(self.compBar.ItemStacksBehindParent)
        self.compBar.setBrush(compBarColor)
        #self.compBar.setBrush(QColor(138, 2, 64))
        self.compBar.setPen(QPen(0))
        
        self.gaugeBar = QGraphicsRectItem(startX, startY, self.maxPixel, height, parent=self.barFrame)
        self.gaugeBar.setFlag(self.gaugeBar.ItemStacksBehindParent)
        self.gaugeBar.setBrush(barColor)
        self.gaugeBar.setPen(QPen(0))
        
        
        self.pixmapNumberList = pixmapNumberList
        self.numSize = self.pixmapNumberList[0].size()
        self.gaugeList = []
        self.maxGaugeList = []
        
        self.setGauge(initGauge, initMaxGauge)
        

    
    def setGauge(self, gauge, maxGauge):
        rect = self.gaugeBar.rect()
        rect.setWidth(self.maxPixel*gauge/maxGauge)
        self.gaugeBar.setRect(rect)
        
        
        for g in self.gaugeList:
            self.scene.removeItem(g)
            del(g)
        self.gaugeList.clear()
            
        for m in self.maxGaugeList:
            self.scene.removeItem(m)
            del(m)
        self.maxGaugeList.clear()
        
        self.gaugeList = self.getDigit(gauge)
        self.maxGaugeList = self.getDigit(maxGauge)
    
        for i in range(len(self.gaugeList)):
            self.gaugeList[i] = QGraphicsPixmapItem(self.gaugeList[i], parent=self.barFrame)
            self.gaugeList[i].setPos(self.pixmap.width()/2 - (i+1)*(self.numSize.width()+2)-8, 0)
        
        self.maxGaugeList.reverse()
        for i in range(len(self.maxGaugeList)):
            self.maxGaugeList[i] = QGraphicsPixmapItem(self.maxGaugeList[i], parent=self.barFrame)
            self.maxGaugeList[i].setPos(self.pixmap.width()/2 + i*(self.numSize.width()+2)+10, 0)
            
        
        
    def getDigit(self, num):
        tmp = num
        numList = []
        if tmp == 0:
            numList.append(self.pixmapNumberList[0])
        else:
            while tmp != 0:
                numList.append(self.pixmapNumberList[tmp % 10])
                tmp = tmp // 10
        return numList
    
    
class chooseSkillWindow():    
    def __init__(self, skillList, scene):
        self.scene = scene
        
        self.background = QGraphicsRectItem(150, 150, config.WIN_WIDTH-300, config.WIN_HEIGHT-300)
        self.background.setBrush(QColor(255, 255, 255))
        self.background.setZValue(15)
        self.scene.addItem(self.background)
        
        self.size = self.background.boundingRect().size()
        
        self.skillList = skillList
        self.candidateList = self.selectRandomSkill(self.skillList)
        self.candidateItem = []
        
        self.selectedSkillNum = 0
        self.rerollNum = 1
        
        font = QFont("함초롬돋움", 30)
        
        for i in range(3):
            rect = QGraphicsRectItem(config.WIN_WIDTH/2+(i-1)*300-100, 250, 200, 350)
            rect.setBrush(QColor(255, 255, 255))
            if i == self.selectedSkillNum:
                rect.setPen(QPen(Qt.black, 3))
            else:
                rect.setPen(QPen(Qt.black, 1))
            titleText = QGraphicsTextItem(self.candidateList[i])
            titleText.setFont(font)
            titleText.setPos(config.WIN_WIDTH/2-titleText.boundingRect().width()/2+(i-1)*300, 300)
            #text.setText()
            group = QGraphicsItemGroup()
            group.setParentItem(self.background)
            group.addToGroup(rect)
            group.addToGroup(titleText)
            self.candidateItem.append(group)
        
        
    def selectRandomSkill(self, skillList):
        return random.sample(skillList, 3)
    
            
    def remove(self):
        for _ in range(3):
            self.scene.removeItem(self.candidateItem[0])
            del self.candidateItem[0]
        self.scene.removeItem(self.background)
        del self.background
        del self


class pauseWindow():
    def __init__(self, scene):
        self.scene = scene
        
        self.background = QGraphicsRectItem(150, 150, config.WIN_WIDTH-300, config.WIN_HEIGHT-300)
        self.background.setBrush(QColor(255, 255, 255))
        self.background.setZValue(15)
        self.scene.addItem(self.background)
        
        self.size = self.background.boundingRect().size()
        
        font = QFont("함초롬돋움", 30)
        self.titleText = QGraphicsTextItem("리플레이 : R")
        self.titleText.setFont(font)
        self.titleText.setPos(config.WIN_WIDTH/2-self.titleText.boundingRect().width()/2, 300)
        self.titleText.setParentItem(self.background)
        
    
    def remove(self):
        self.scene.removeItem(self.titleText)
        del self.titleText
        self.scene.removeItem(self.background)
        del self.background
        del self
        