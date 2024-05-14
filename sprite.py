# -*- coding: utf-8 -*-
from PyQt5.QtGui import *

class Sprite():
    def __init__(self):
        self.zombieFrontMoveList = [QPixmap("./img/virus/front_move_" + str(i+1) + ".png") for i in range(6)]
        self.zombieBackMoveList = [QPixmap("./img/virus/back_move_" + str(i+1) + ".png") for i in range(6)]
        self.zombieRightMoveList = [QPixmap("./img/virus/beside_move_" + str(i+1) + ".png") for i in range(6)]
        self.zombieLeftMoveList = [pm.transformed(QTransform().scale(-1, 1)) for pm in self.zombieRightMoveList]
        
        #eff = QGraphicsColorizeEffect()
        #eff.setColor(QColor(223,0,0))
        self.zombieDamageFrontMoveList = [self.imageColorized(item) for item in self.zombieFrontMoveList]
        self.zombieDamageBackMoveList = [self.imageColorized(item) for item in self.zombieBackMoveList]
        self.zombieDamageRightMoveList = [self.imageColorized(item) for item in self.zombieRightMoveList]
        self.zombieDamageLeftMoveList = [self.imageColorized(item) for item in self.zombieLeftMoveList]
        
        self.zombieDeathList = [QPixmap("./img/virus/dead_" + str(i+1) + ".png") for i in range(6)]
        
        self.electromagneticList = [QPixmap("./img/effect/electromagnetic/electric_" + str(i+1) + ".png") for i in range(6)]
        self.bulletSprite = QPixmap("./img/bullet.png")
        self.droneList = [QPixmap("./img/effect/drone/drone_" + str(i+1) + ".png") for i in range(2)]

        self.damageNumberList = [QPixmap("./img/number/damage_" + str(i) + ".png") for i in range(10)]
        self.timeColon = QPixmap("./img/number/time_colon.png")
        self.timeNumberList = [QPixmap("./img/number/time_" + str(i) + ".png") for i in range(10)]
        self.scoreNumberList = [QPixmap("./img/number/score_" + str(i) + ".png") for i in range(10)]
        self.hpBarSprite = QPixmap("./img/UI/HP_bar.png")
        self.hpNumberList = [QPixmap("./img/number/HP_" + str(i) + ".png") for i in range(10)]
        self.expBarSprite = QPixmap("./img/UI/EXP_bar.png")
        self.expNumberList = [QPixmap("./img/number/EXP_" + str(i) + ".png") for i in range(10)]
        
    
    def imageColorized(self, qpixmap, choice="red"):
        img = QImage(qpixmap.toImage())
        for x in range(img.size().width()):
            for y in range(img.size().height()):
                curColor = QColor(img.pixel(x, y))
                if curColor.red()+curColor.green()+curColor.blue()==0:
                    curColor.setAlpha(0)
                else:
                    grey = (curColor.red()*11 + curColor.green() * 16 + curColor.blue()*5)/32 #color scale > grey scale
                    grey = min(grey*1.5, 255)
                    curColor.setRed(grey*0.94)
                    curColor.setGreen(grey*0.113)
                    curColor.setBlue(grey*0.096)
                
                img.setPixel(x, y, curColor.rgba())
                
        return QPixmap.fromImage(img)