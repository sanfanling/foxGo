#!/bin/use/python

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtMultimedia import QSound
import os
import goEngine
import sgfData
from board import board
from txwq import txwq
from sinawq import sinawq
import subprocess
from myThread import getOutputThread
from configration import configration
from configparser import ConfigParser
from searchLocal import searchLocal
from startAiDialog import startAiDialog

class mainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        
        cf = ConfigParser()
        cf.read(os.path.expanduser("~/.config/foxGo.conf"))
        self.sgfPath = os.path.expanduser(cf.get("Path", "sgfpath"))
        if cf.get("Download", "autoskip").lower() == "true":
            self.autoSkip = True
        else:
            self.autoSkip = False
        if cf.get("Download", "saveas").lower() == "true":
            self.saveAs = True
        else:
            self.saveAs = False
        self.address = cf.get("Gnugo", "address")
        self.port = cf.get("Gnugo", "port")
        if cf.get("Board", "handcounts").lower() == "true":
            self.handcounts = True
        else:
            self.handcounts = False
        self.style = cf.get("Board", "style")
        if cf.get("Board", "coordinate").lower() == "true":
            self.coordinate = True
        else:
            self.coordinate = False
        if cf.get("Sound", "music").lower() == "true":
            self.music = True
        else:
            self.music = False
        if cf.get("Sound", "effect").lower() == "true":
            self.effect = True
        else:
            self.effect = False
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setWindowTitle("foxGo")
        self.setWindowIcon(QIcon("res/logo.png"))
        self.setUi()
        self.showMaximized()
        self.startFreeMode()
        self.initInfoLabel()

        self.fileOpen.triggered.connect(self.getFile)
        self.newGame.triggered.connect(self.newGame_)
        self.ai.triggered.connect(self.startAiMode)
        self.printGo.triggered.connect(self.printGo_)
        self.printGoPreview.triggered.connect(self.printGoPreview_)
        self.previousToStart.clicked.connect(self.previousToStart_)
        self.previous10Steps.clicked.connect(self.previous10Steps_)
        self.next10Steps.clicked.connect(self.next10Steps_)
        self.nextToEnd.clicked.connect(self.nextToEnd_)
        self.nextStep.clicked.connect(self.nextStep_)
        self.previousStep.clicked.connect(self.previousStep_)
        self.backToPoint.clicked.connect(self.backToPoint_)
        self.commentBox.anchorClicked.connect(self.showVariation)
        self.stepsCount.editingFinished.connect(self.gotoSpecifiedStep)
        self.stepsSlider.valueChanged.connect(self.stepsCount.setValue)
        self.stepsSlider.sliderReleased.connect(self.gotoSpecifiedStep)
        self.settingAction.triggered.connect(self.settingAction_)
        self.foxAction.triggered.connect(self.foxAction_)
        self.sinaAction.triggered.connect(self.sinaAction_)
        self.searchAction.triggered.connect(self.searchAction_)
        self.quit.triggered.connect(self.close)
        self.aboutQt.triggered.connect(self.aboutQt_)
        self.aboutApp.triggered.connect(self.aboutApp_)
        
        self.styleGroup.triggered.connect(self.changeBoardStyle)
        self.withCoordinate.toggled.connect(self.withCoordinate_)
        
        self.showHands.triggered.connect(self.board.update)
        
    def setUi(self):        
        self.menuBar = QMenuBar(self)
        
        gameMenu = self.menuBar.addMenu("Game")
        self.newGame = QAction("New")
        self.fileOpen = QAction("Open...")
        self.ai = QAction("AI mode (beta)")
        gameMenu.addAction(self.newGame)
        gameMenu.addAction(self.fileOpen)
        gameMenu.addAction(self.ai)
        gameMenu.addSeparator()
        self.printGo = QAction("Print...")
        self.printGoPreview = QAction("Preview...")
        gameMenu.addAction(self.printGo)
        gameMenu.addAction(self.printGoPreview)
        gameMenu.addSeparator()
        self.quit = QAction("Quit")
        gameMenu.addAction(self.quit)
        
        dispalyMenu = self.menuBar.addMenu("Display")
        self.showHands = QAction("Handcounts")
        self.showHands.setCheckable(True)
        self.showHands.setChecked(self.handcounts)
        dispalyMenu.addAction(self.showHands)
        self.withCoordinate = QAction("Coordinate")
        self.withCoordinate.setCheckable(True)
        self.withCoordinate.setChecked(self.coordinate)
        dispalyMenu.addAction(self.withCoordinate)
        boardStyleMenu = dispalyMenu.addMenu("Board style")
        self.styleGroup = QActionGroup(self)
        self.boardStyle1 = QAction("Style1")
        self.boardStyle2 = QAction("Style2")
        self.boardStyle1.setCheckable(True)
        self.boardStyle2.setCheckable(True)
        if self.style == "style1":
            self.boardStyle1.setChecked(True)
        elif self.style == "style2":
            self.boardStyle2.setChecked(True)
        self.styleGroup.addAction(self.boardStyle1)
        self.styleGroup.addAction(self.boardStyle2)
        boardStyleMenu.addAction(self.boardStyle1)
        boardStyleMenu.addAction(self.boardStyle2)
        
        soundMenu = self.menuBar.addMenu("Sound")
        self.musicAction = QAction("Music")
        self.musicAction.setCheckable(True)
        self.musicAction.setChecked(self.music)
        self.soundEffect = QAction("Sound Effect")
        self.soundEffect.setCheckable(True)
        self.soundEffect.setChecked(self.effect)
        soundMenu.addAction(self.musicAction)
        soundMenu.addAction(self.soundEffect)
        
        websgfMenu = self.menuBar.addMenu("Web sgf")
        self.foxAction = QAction("Download from Tx Weiqi...")
        self.sinaAction = QAction("Download from Sina Weiqi...")
        self.searchAction = QAction("Search local sgf...")
        websgfMenu.addAction(self.foxAction)
        websgfMenu.addAction(self.sinaAction)
        websgfMenu.addAction(self.searchAction)
        
        settingMenu = self.menuBar.addMenu("Configration")
        self.settingAction = QAction("Configrate foxGo...")
        settingMenu.addAction(self.settingAction)
        
        helpMenu = self.menuBar.addMenu("Help")
        self.aboutApp = QAction("About foxGo...")
        self.aboutQt = QAction("About Qt...")
        helpMenu.addAction(self.aboutApp)
        helpMenu.addAction(self.aboutQt)
        
        hlayout = QHBoxLayout(None)
        self.previousToStart = QPushButton("|<", self)
        self.previous10Steps = QPushButton("<<", self)
        self.previousStep = QPushButton("<", self)
        self.stepsCount = QSpinBox(self)
        self.stepsCount.setMinimum(0)
        self.nextStep = QPushButton(">", self)
        self.next10Steps = QPushButton(">>", self)
        self.nextToEnd = QPushButton(">|", self)
        self.backToPoint = QPushButton("Back", self)
        self.backToPoint.setEnabled(False)
        self.stepsSlider = QSlider(self)
        self.stepsSlider.setTracking(True)
        self.stepsSlider.setOrientation(Qt.Horizontal)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.stepsSlider.setSizePolicy(sizePolicy)
        
        self.otherButton = QPushButton("Other", self)
        otherMenu = QMenu(self)
        self.passAction = QAction("Pass", self)
        self.resignAction = QAction("Resign", self)
        otherMenu.addAction(self.passAction)
        otherMenu.addAction(self.resignAction)
        self.otherButton.setMenu(otherMenu)
        
        hlayout.addWidget(self.previousToStart)
        hlayout.addWidget(self.previous10Steps)
        hlayout.addWidget(self.previousStep)
        hlayout.addWidget(self.stepsCount)
        hlayout.addWidget(self.nextStep)
        hlayout.addWidget(self.next10Steps)
        hlayout.addWidget(self.nextToEnd)
        hlayout.addWidget(self.backToPoint)
        hlayout.addWidget(self.otherButton)
        hlayout.addWidget(self.stepsSlider)

        hlayout_1 = QHBoxLayout(None)
        vlayout = QVBoxLayout(None)
        vlayout.setContentsMargins(0, 30, 0, 30)
        self.playerLabel = QLabel(self)
        font = self.playerLabel.font()
        font.setBold(True)
        font.setPointSize(20)
        self.playerLabel.setFont(font)
        self.gameInfo = QLabel(self)
        self.commentLabel = QLabel("Comments", self)
        self.commentBox = QTextBrowser(self)
        self.commentBox.setOpenLinks(False)
        vlayout.addWidget(self.playerLabel)
        vlayout.addWidget(self.gameInfo)
        vlayout.addWidget(self.commentLabel)
        vlayout.addWidget(self.commentBox)
        vlayout.setStretch(0, 1)
        vlayout.setStretch(1, 5)
        vlayout.setStretch(2, 0)
        vlayout.setStretch(3, 10)
        
        self.board = board(self)
        
        horizontalSpacer1 = QSpacerItem(30, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout_1.addItem(horizontalSpacer1)
        hlayout_1.addWidget(self.board)
        hlayout_1.addItem(horizontalSpacer1)
        hlayout_1.addLayout(vlayout)
        hlayout_1.setStretch(0, 1)
        hlayout_1.setStretch(1, 0)
        hlayout_1.setStretch(2, 1)
        hlayout_1.setStretch(3, 10)
        
        self.statusBar = QStatusBar(self)
        self.coordLabel = QLabel("Mouse coordinate: 0,0    Board coordinate: 0,0    Go coordinate: 0,0", self)
        self.coordLabel.setAlignment(Qt.AlignLeft)
        self.modeLabel = QLabel(self)
        self.modeLabel.setAlignment(Qt.AlignRight)
        self.statusBar.addPermanentWidget(self.coordLabel, 5)
        self.statusBar.addPermanentWidget(self.modeLabel, 1)
        
        mainLayout = QVBoxLayout(None)
        mainLayout.setContentsMargins(30, 0, 80, 0)
        mainLayout.addWidget(self.menuBar)
        mainLayout.addLayout(hlayout_1)
        mainLayout.addLayout(hlayout)
        mainLayout.addWidget(self.statusBar)
        self.setLayout(mainLayout)
        mainLayout.setStretch(0, 0)
        mainLayout.setStretch(1, 1)
        mainLayout.setStretch(2, 0)
        mainLayout.setStretch(3, 0)
    
    
    def showStepsCount(self, setMaximum = False):
        if setMaximum:
            self.stepsCount.setMaximum(self.stepPoint - self.breakPoint)
            self.stepsSlider.setMaximum(self.stepPoint - self.breakPoint)
        self.stepsCount.setValue(self.stepPoint - self.breakPoint)
        self.stepsSlider.setValue(self.stepPoint - self.breakPoint)
    
    def startAiMode(self):
        aiDialog = startAiDialog(self)
        if aiDialog.exec_() == QDialog.Accepted:
            self.mode = "ai"
            self.commentBox.clear()
            self.stepPoint = 0
            self.breakPoint = 0
            self.showStepsCount(True)
            self.modeLabel.setText("Now is in AI mode")
            self.thisGame = goEngine.go()
            self.board.update()
            if aiDialog.blackStone.isChecked():
                self.peopleColor = "black"
            else:
                self.peopleColor = "white"
            self.goSocket = aiDialog.goSocket
        
    
    def communicateAi(self):
        self.waitAi = getOutputThread(self)
        self.waitAi.finished.connect(self.makeAiMove)
        self.waitAi.start()
        
    def makeAiMove(self):
        moveSuccess , deadChessNum = self.thisGame.makeStepSafe()
        self.stepPoint += 1
        self.showStepsCount(True)
        self.board.update()
        self.makeSound(moveSuccess, deadChessNum)
        self.thisGame.changeColor()
    
    def startFreeMode(self):
        self.mode = "free"
        self.commentBox.clear()
        self.stepPoint = 0
        self.breakPoint = 0
        #self.clearLength = 0
        self.thisGame = goEngine.go()
        self.showStepsCount(True)
        self.modeLabel.setText("Now is in free mode")
    
    def restartFreeAndTestMode(self):
        self.thisGame.stepsGo = self.thisGame.stepsGo[:self.stepPoint]
        self.reviewMove()
    
    def startTestMode(self, vl = []):
        self.mode = "test"
        self.commentBox.clear()
        self.modeLabel.setText("Current mode: Test")
        self.breakPoint = self.stepPoint
        self.stepsGo_original = list(self.thisGame.stepsGo)
        #self.clearLength = len(self.thisGame.stepsGoDict)
        self.thisGame.stepsGo = self.thisGame.stepsGo[:self.stepPoint] + vl
        self.stepPoint += len(vl)
        #self.showStepsCount()
        self.reviewMove()
        self.backToPoint.setEnabled(True)
        
    def startReviewMode(self, f):
        self.mode = "review"
        self.commentBox.clear()
        self.modeLabel.setText("Current mode: Review")
        self.sgfEngine = sgfData.sgfData(f)
        self.thisGame = goEngine.go()
        self.thisGame.stepsGo = self.sgfEngine.getStepsData(self.sgfEngine.rest)
        self.commentDict = self.sgfEngine.getCommentsData(self.sgfEngine.rest)
        self.variations = self.sgfEngine.getVariations()
        self.getPlayersInfo()
        self.getGameInfo()
        self.stepPoint = len(self.thisGame.stepsGo)
        self.stepsCount.setRange(0, self.stepPoint)
        self.stepsSlider.setRange(0, self.stepPoint)
        self.showStepsCount()
        self.reviewMove()
    
    def getGameInfo(self):
        game = "Game: %s\n\n" %(self.sgfEngine.getTitle(),)
        date = "Date: %s\n\n" %(self.sgfEngine.getDate(),)
        komi = "Komi: %s\n\n" %(self.sgfEngine.getKomi(),)
        result = "Result: %s\n" %(self.sgfEngine.getResult(),)
        self.gameInfo.setText(game + date + komi + result)
    
    def getPlayersInfo(self):
        Pb = "Black: %s                   %s\n\n" %(self.sgfEngine.getBlackPlayer(), self.sgfEngine.getBlackPlayerDan())
        Pw = "White: %s                   %s\n" %(self.sgfEngine.getWhitePlayer(), self.sgfEngine.getWhitePlayerDan())
        self.playerLabel.setText(Pb+Pw)
    
    def initInfoLabel(self):
        self.gameInfo.setText("Game: N/A\n\nDate: N/A\n\nKomi: N/A\n\nResult: N/A\n")
        self.playerLabel.setText("Black:   N/A\n\nWhite:   N/A\n")
    
    def backToPoint_(self):
        self.mode = "review"
        self.commentBox.clear()
        self.modeLabel.setText("Current mode: Review")
        self.thisGame.stepsGo = self.stepsGo_original
        self.stepPoint = self.breakPoint
        self.breakPoint = 0
        self.stepsCount.setMaximum(len(self.thisGame.stepsGo))
        self.stepsSlider.setMaximum(len(self.thisGame.stepsGo))
        self.showStepsCount()
        self.reviewMove()
        self.backToPoint.setEnabled(False)
    
    def getFile(self):
        fileName, y = QFileDialog.getOpenFileName(self, "Open a SGF file", self.sgfPath, "Go records file(*.sgf)")
        if fileName:
            self.startReviewMode(fileName)
    
    def newGame_(self):
        self.startFreeMode()
        self.initInfoLabel()
        self.board.update()
    
    def printGo_(self):
        printer = QPrinter()
        printDialog = QPrintDialog(printer, self)
        if printDialog.exec_() == QDialog.Accepted:
            self.handlePaintRequest(printer)
    
    def printGoPreview_(self):
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()
    
    def handlePaintRequest(self, printer):
        painter = QPainter(printer)
        rect = painter.viewport()
        pix = self.board.grab(self.board.rect())
        size = pix.size()
        size.scale(rect.size(), Qt.KeepAspectRatio)
        painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        painter.setWindow(pix.rect())
        painter.drawPixmap(0, 0, pix)
    
    def gotoSpecifiedStep(self):
        self.stepPoint = self.stepsCount.value() + self.breakPoint
        self.stepsSlider.setValue(self.stepsCount.value())
        self.reviewMove()
    
    def previousToStart_(self):
        self.stepPoint = self.breakPoint
        self.showStepsCount()
        self.reviewMove()
    
    def previous10Steps_(self):
        if self.stepPoint - 10 >= self.breakPoint:
               self.stepPoint -= 10
        else:
            self.stepPoint = self.breakPoint
        self.showStepsCount()
        self.reviewMove()
    
    def previousStep_(self):
        if self.stepPoint - 1 >= self.breakPoint:
            self.stepPoint -= 1
            self.showStepsCount()
            self.reviewMove()
    
    def nextStep_(self):
        if self.stepPoint + 1 <= len(self.thisGame.stepsGo):
            self.stepPoint += 1
            self.showStepsCount()
            self.reviewMove()

    def next10Steps_(self):
        if self.stepPoint + 10 < len(self.thisGame.stepsGo):
            self.stepPoint += 10
        else:
            self.stepPoint = len(self.thisGame.stepsGo)
        self.showStepsCount()
        self.reviewMove()
    
    def nextToEnd_(self):
        self.stepPoint = len(self.thisGame.stepsGo)
        self.showStepsCount()
        self.reviewMove()
    
    def reviewMove(self):
        self.thisGame.stepsGoDict = {}
        tmpList = self.thisGame.stepsGo[:self.stepPoint]
        if len(tmpList) != 0:
            for i, c, x, y in tmpList:
                self.thisGame.stepNum = i
                self.thisGame.goColor = c
                self.thisGame.x = x
                self.thisGame.y = y
                moveSuccess, deadChessNum = self.thisGame.makeStepSafe()
            self.board.update()
            self.makeSound(moveSuccess, deadChessNum)
            
            self.thisGame.changeColor()
            
        else:
            self.thisGame.goColor = "black"
            self.board.update()

        
        if self.mode == "review":
            if self.stepPoint in self.commentDict:
                self.commentBox.setPlainText(self.commentDict[self.stepPoint])
            else:
                self.commentBox.clear()
            
            if self.stepPoint in self.variations:
                self.commentBox.moveCursor(QTextCursor.End)
                self.commentBox.insertHtml(self.formatVariation())
    
    def formatVariation(self):
        p = 0
        text = "<br><br>"
        for i in self.variations[self.stepPoint]:
            p += 1
            co = i[-1]
            title = "Variation: %d-%d" %(self.stepPoint, p)
            text += '<a href="%s">%s</a> %s<br>' %(title, title, co)
        return text
            
    def showVariation(self, link):
        #self.commentBox.clear()
        name = link.fileName().strip()
        point, num = name.split("-")
        point = int(point)
        num = int(num)
        vl = self.variations[point][num-1][:-1]
        self.startTestMode(vl)
        self.showStepsCount(True)
    
    def changeBoardStyle(self, action):
        if "1" in action.text():
            if self.withCoordinate.isChecked():
                self.board.setBoard("yboard-y.png")
            else:
                self.board.setBoard("yboard-n.png")
        elif "2" in action.text():
            if self.withCoordinate.isChecked():
                self.board.setBoard("bboard-y.png")
            else:
                self.board.setBoard("bboard-n.png")
    
    def withCoordinate_(self, b):
        if self.boardStyle1.isChecked() and b:
            b = "yboard-y.png"
            size = QSize(665, 665)
        elif self.boardStyle1.isChecked() and not b:
            b = "yboard-n.png"
            size = QSize(649, 649)
        elif self.boardStyle2.isChecked() and b:
            b = "bboard-y.png"
            size = QSize(665, 665)
        elif self.boardStyle2.isChecked() and not b:
            b = "bboard-n.png"
            size = QSize(649, 649)
        self.board.setSize(size)
        self.board.setBoard(b)
    
    def makeSound(self, moveSuccess, deadChessNum):
        if not self.soundEffect.isChecked() or moveSuccess == 0:
            return
        else:
            if moveSuccess == 1:
                soundFile = "res/sound/112.wav"
            elif moveSuccess == 2:
                if deadChessNum == 1:
                    soundFile = "res/sound/105.wav"
                elif 2 <= deadChessNum < 10:
                    soundFile = "res/sound/104.wav"
                else:
                    soundFile = "res/sound/103.wav"
        sound = QSound(soundFile, self)
        sound.play()
    
    def settingAction_(self):
        self.configDialog = configration()
        self.configDialog.path.lineEdit.setText(self.sgfPath)
        self.configDialog.download.autoSkip.setChecked(self.autoSkip)
        if self.saveAs:
            self.configDialog.download.saveAs.setChecked(True)
        else:
            self.configDialog.download.autoCover.setChecked(True)
        self.configDialog.gnugo.address.setText(self.address)
        self.configDialog.gnugo.port.setText(self.port)
        
        if self.configDialog.exec_() == QDialog.Accepted:
            self.sgfPath = self.configDialog.path.lineEdit.text()
            self.autoSkip = self.configDialog.download.autoSkip.isChecked()
            self.saveAs = self.configDialog.download.saveAs.isChecked()
            self.address = self.configDialog.gnugo.address.text()
            self.port = self.configDialog.gnugo.port.text()
        
        txDir = os.path.join(self.sgfPath, "txwq")
        if not os.path.isdir(txDir):
            os.makedirs(txDir)
        
        sinaDir = os.path.join(self.sgfPath, "sinawq")
        if not os.path.isdir(sinaDir):
            os.makedirs(sinaDir)
    
    def foxAction_(self):
        self.tx = txwq(self)
        self.tx.show()
    
    def sinaAction_(self):
        self.sina = sinawq(self)
        self.sina.show()
    
    def searchAction_(self):
        self.searchBox = searchLocal(self)
        self.searchBox.show()
    
    def aboutQt_(self):
        QMessageBox.aboutQt(self, "About Qt")
    
    def aboutApp_(self):
        QMessageBox.about(self, "About foxGo", "Enjoy Go's magic with foxGo under Linux environment")
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Right or e.key() == Qt.Key_Down or e.key() == Qt.Key_Space:
            self.nextStep_()
        elif e.key() == Qt.Key_Left or e.key() == Qt.Key_Up:
            self.previousStep_()
        elif e.key() == Qt.Key_Home:
            self.previousToStart_()
        elif e.key() == Qt.Key_End:
            self.nextToEnd_()
        elif e.key() == Qt.Key_PageUp:
            self.previous10Steps_()
        elif e.key() == Qt.Key_PageDown:
            self.next10Steps_()
        elif e.key() == Qt.Key_Escape:
            self.backToPoint_()
    
    def closeEvent(self, e):
        cf = ConfigParser()
        cf.read(os.path.expanduser("~/.config/foxGo.conf"))
        cf.set("Path", "sgfpath", self.sgfPath)
        if self.autoSkip:
            cf.set("Download", "autoskip", "True")
        else:
            cf.set("Download", "autoskip", "False")
        if self.saveAs:
            cf.set("Download", "saveas", "True")
        else:
            cf.set("Download", "saveas", "False")
        
        cf.set("Gnugo", "address", self.address)
        cf.set("Gnugo", "port", self.port)
        if self.showHands.isChecked():
            cf.set("Board", "handcounts", "True")
        else:
            cf.set("Board", "handcounts", "False")
        if self.boardStyle1.isChecked():
            cf.set("Board", "style", "style1")
        elif self.boardStyle2.isChecked():
            cf.set("Board", "style", "style2")
        if self.withCoordinate.isChecked():
            cf.set("Board", "coordinate", "True")
        else:
            cf.set("Board", "coordinate", "False")
        if self.musicAction.isChecked():
            cf.set("Sound", "music", "True")
        else:
            cf.set("Sound", "music", "False")
        if self.soundEffect.isChecked():
            cf.set("Sound", "effect", "True")
        else:
            cf.set("Sound", "effect", "False")
        f = open(os.path.expanduser("~/.config/foxGo.conf"), 'w')
        cf.write(f)
        f.close()
        
        e.accept()
