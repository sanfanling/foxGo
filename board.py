#! /usr/bin/python


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class board(QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.inBoard = False
        self.tmpx = 0
        self.tmpy = 0
        self.setMouseTracking(True)
        if self.parent.boardStyle1.isChecked() and self.parent.withCoordinate.isChecked():
            b = "yboard-y.png"
            size = QSize(665, 665)
        elif self.parent.boardStyle1.isChecked() and not self.parent.withCoordinate.isChecked():
            b = "yboard-n.png"
            size = QSize(649, 649)
        elif self.parent.boardStyle2.isChecked() and self.parent.withCoordinate.isChecked():
            b = "bboard-y.png"
            size = QSize(665, 665)
        elif self.parent.boardStyle2.isChecked() and not self.parent.withCoordinate.isChecked():
            b = "bboard-n.png"
            size = QSize(649, 649)
        self.setSize(size)
        self.setBoard(b)
    
    def setSize(self, size):
        if self.parent.withCoordinate.isChecked():
            self.setFixedSize(QSize(665, 665))
        else:
            self.setFixedSize(QSize(649, 649))
    
    def setBoard(self, boardStyle):
        bg = QPixmap('res/%s' %(boardStyle,))
        palette = self.palette()
        palette.setColor(QPalette.Background, Qt.black)
        self.setAutoFillBackground(True)
        palette.setBrush(QPalette.Window, QBrush(bg))
        self.setPalette(palette)
    
    def enterEvent(self, e):
        self.inBoard = True
        self.update()
    
    def leaveEvent(self, e):
        self.inBoard = False
        self.update()
    
    def mouseMoveEvent(self, e):
        self.parent.thisGame.x, self.parent.thisGame.y = self.posMapToGo(e.pos().x(), e.pos().y())
        (boardx, boardy) = self.goMapToBorad(self.parent.thisGame.x, self.parent.thisGame.x)
        self.parent.coordLabel.setText("application coordinate: %d,%d      board coordinate: %d,%d      go coordinate: %d,%d" %(e.pos().x(), e.pos().y(), boardx, boardy, self.parent.thisGame.x, self.parent.thisGame.y))
        if (self.parent.thisGame.x, self.parent.thisGame.y) != (self.tmpx, self.tmpy):
            self.tmpx = self.parent.thisGame.x
            self.tmpy = self.parent.thisGame.y
            self.update()
    
    def mousePressEvent(self, e):
        px, py = self.posMapToGo(e.pos().x(), e.pos().y())
        hasStone = (px, py) in self.parent.thisGame.stepsGoDict.keys()
        
        if e.button() == Qt.LeftButton and self.parent.mode == "free" and not hasStone:
            if self.parent.stepPoint != len(self.parent.thisGame.stepsGo):
                self.parent.restartFreeAndTestMode()
            self.parent.thisGame.x, self.parent.thisGame.y = px, py
            moveSuccess, deadChessNum = self.parent.thisGame.makeStep()
            if moveSuccess:
                self.parent.stepPoint += 1
                self.parent.showStepsCount(True)
                self.update()
                self.parent.makeSound(moveSuccess, deadChessNum)
                
        elif e.button() == Qt.LeftButton and self.parent.mode == "review" and not hasStone:
            self.parent.startTestMode()
            self.parent.thisGame.stepNum = 0
            self.parent.thisGame.x, self.parent.thisGame.y = px, py
            moveSuccess, deadChessNum = self.parent.thisGame.makeStep()
            if moveSuccess:
                self.parent.stepPoint += 1
                self.parent.showStepsCount(True)
                self.update()
                self.parent.makeSound(moveSuccess, deadChessNum)
                
        elif e.button() == Qt.LeftButton and self.parent.mode == "test" and not hasStone:
            if self.parent.stepPoint != len(self.parent.thisGame.stepsGo):
                self.parent.restartFreeAndTestMode()
            self.parent.thisGame.x, self.parent.thisGame.y = px, py
            moveSuccess, deadChessNum = self.parent.thisGame.makeStep()
            if moveSuccess:
                self.parent.stepPoint += 1
                self.parent.showStepsCount(True)
                self.update()
                self.parent.makeSound(moveSuccess, deadChessNum)
            
        elif e.button() == Qt.LeftButton and self.parent.mode == "ai" and not hasStone:
            if self.parent.thisGame.goColor == self.parent.peopleColor:
                self.parent.thisGame.x, self.parent.thisGame.y = px, py
                moveSuccess, deadChessNum = self.parent.thisGame.makeStep()
                if moveSuccess:
                    self.parent.stepPoint += 1
                    self.parent.showStepsCount(True)
                    self.repaint()
                    self.parent.makeSound(moveSuccess, deadChessNum)
                    print("People move: {0},{1}".format(self.parent.thisGame.x, self.parent.thisGame.y))
                    self.parent.communicateAi("play")
    
    def paintEvent(self, e):
        p = QPainter()
        p.begin(self)
        
        for hax, hay in self.parent.thisGame.ha:
            board_hax, board_hay =  self.goMapToBorad(hax, hay)
            p.drawPixmap(board_hax-15, board_hay-15, QPixmap("res/blackStone.png"))
        
        for x, y in list(self.parent.thisGame.stepsGoDict.keys()):
            if self.parent.thisGame.stepsGoDict[(x, y)][0] == "black":
                pix = QPixmap("res/blackStone.png")
                col_tmp = Qt.white
            else:
                pix = QPixmap("res/whiteStone.png")
                col_tmp = Qt.black
            (x2, y2) = self.goMapToBorad(x, y)
            p.drawPixmap(x2-15, y2-15, pix)
            
            if self.parent.stepNumberAll.isChecked():
                count = self.parent.thisGame.stepsGoDict[(x, y)][1]
                if count == 0:
                    continue
                if self.checkClearCount((x, y)):
                    p.setPen(QPen(col_tmp))
                    font = p.font()
                    font.setBold(True)
                    p.setFont(font)
                    rect = QRect(x2-15, y2-15, 30, 30)
                    p.drawText(rect, Qt.AlignCenter, str(count))
                    
            elif self.parent.stepNumberCurrent.isChecked():
                count = self.parent.thisGame.stepsGoDict[(x, y)][1]
                _x1, _y1 = list(self.parent.thisGame.stepsGoDict.keys())[-1]
                _x1, _y1 = self.goMapToBorad(_x1, _y1)
        
        if len(self.parent.thisGame.stepsGoDict) != 0:
            _x, _y = list(self.parent.thisGame.stepsGoDict.keys())[-1]
            _x, _y = self.goMapToBorad(_x, _y)
            if count != 0:
                if self.parent.stepNumberCurrent.isChecked():
                    if list(self.parent.thisGame.stepsGoDict.values())[-1][0] == "black":
                        current_cl = Qt.white
                    else:
                        current_cl = Qt.black
                    p.setPen(QPen(current_cl))
                    font = p.font()
                    font.setBold(True)
                    p.setFont(font)
                    rect = QRect(_x-15, _y-15, 30, 30)
                    p.drawText(rect, Qt.AlignCenter, str(count))
                else:
                    tp = QPixmap("res/current.png")
                    p.drawPixmap(_x-15, _y-15, tp)
            
        if (self.parent.thisGame.x, self.parent.thisGame.y) not in self.parent.thisGame.stepsGoDict.keys() and self.inBoard:
            (x1, y1) = self.goMapToBorad(self.parent.thisGame.x, self.parent.thisGame.y)
            p.setBrush(QBrush(Qt.white, Qt.SolidPattern))
            p.drawRect(x1-6, y1-6, 12, 12)
            
        p.end()
            
    def checkClearCount(self, currentKey):
        keyList = list(self.parent.thisGame.stepsGoDict.keys())
        valueList = list(map(lambda x: x[1], list(self.parent.thisGame.stepsGoDict.values())))
        ind = keyList.index(currentKey)
        count = valueList[ind]
        for i in valueList[ind+1:]:
            if count >= i:
                return False
        return True
    
    def posMapToGo(self, a, b):
        x = round((a+16)/34)
        y = round((b+16)/34)
        if x > 19:
            x = 19
        if x < 1:
            x = 1
        if y > 19:
            y = 19
        if y < 1:
            y = 1
        return (x, y)
    
    def goMapToBorad(self, a, b):
        return (a*34-16, b*34-16)
    
    def boardMapToGo(self, a, b):
        return ((a+16)/34, (b+16)/34)
    
    
