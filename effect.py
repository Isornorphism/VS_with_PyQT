# -*- coding: utf-8 -*-
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, QVariantAnimation, QTimeLine, QEasingCurve
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsItemGroup

class damageEffect():
    def __init__(self, parentItem, damage, pixmapList, scene):
        self.parentItem = parentItem
        self.scene = scene
        #self.numberList = []
        self.numberGroup = QGraphicsItemGroup()
        
        #self.pixmapList = [QPixmap("./img/number/damage_" + str(i) + ".png") for i in range(10)]
        self.size = pixmapList[0].size()
        self.effHeight = 30
        
        self.animation = QVariantAnimation()
        self.animation.valueChanged.connect(self.handle_valueChanged)
        self.animation.setEasingCurve(QEasingCurve.OutQuart) # InCubic, InQuart, InQuint, InCirc
        self.animation.setDuration(1000)
        self.animation.finished.connect(self.remove)
        self.animation.finished.connect(self.parentItem.removeEffect)
        
        tmp = damage
        numberList = []
        if tmp == 0:
            for _ in range(1):
                numberList.append(pixmapList[0])
        else:
            digit = 0
            while tmp != 0:
                numberList.append(pixmapList[tmp % 10])
                tmp = tmp // 10
                digit += 1
           
        numberList.reverse()
        for i in range(digit):
            numberList[i] = QGraphicsPixmapItem(numberList[i])
            numberList[i].setPos((-digit+2*i)*self.size.width()/2, 0)
            self.numberGroup.addToGroup(numberList[i])
            
        self.numberGroup.setParentItem(self.parentItem)
        #eff.setColor(QColor(0,255,0))
        #print(self.numberGroup.graphicsEffect())
        self.animation.setStartValue(QPointF(0, -self.parentItem.size/2-3))
        self.animation.setEndValue(QPointF(0, -self.parentItem.size/2-3-self.effHeight))
        self.animation.start()
        
        
    def handle_valueChanged(self, value):
        if hasattr(self, 'numberGroup'):
            self.numberGroup.setPos(value)
    
    def remove(self):
        if hasattr(self, 'numberGroup'):
            self.scene.removeItem(self.numberGroup)
            del self.numberGroup
        del self
            
            
            