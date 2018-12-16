#!/bin/use/python

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtMultimedia import QSoundEffect, QSound
import os
import goEngine
import sgfData
from board import board
from txwq import txwq
from sinawq import sinawq
from cyberoro import cyberoro
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
        self.stepNumber = cf.get("Board", "stepnumber")
        self.style = cf.get("Board", "style")
        if cf.get("Board", "coordinate").lower() == "true":
            self.coordinate = True
        else:
            self.coordinate = False
        self.musicPath = cf.get("Sound", "musicpath")
        if cf.get("Sound", "music").lower() == "true" and self.musicPath:
            self.music = True
        else:
            self.music = False
        
        if cf.get("Sound", "effect").lower() == "true":
            self.effect = True
        else:
            self.effect = False
        
        self.backgroundMusic = QSound(self.musicPath, self)
        self.backgroundMusic.setLoops(99)
        #self.backgroundMusic.setLoops(-1)
        self.stoneSound = QSoundEffect(self)
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
        self.quitAction.triggered.connect(self.quitAction_)
        self.commentBox.anchorClicked.connect(self.showVariation)
        self.stepsCount.editingFinished.connect(self.gotoSpecifiedStep)
        self.stepsSlider.valueChanged.connect(self.stepsCount.setValue)
        self.stepsSlider.sliderReleased.connect(self.gotoSpecifiedStep)
        self.settingAction.triggered.connect(self.settingAction_)
        self.foxAction.triggered.connect(self.foxAction_)
        self.sinaAction.triggered.connect(self.sinaAction_)
        self.cyberoroAction.triggered.connect(self.cyberoroAction_)
        self.searchAction.triggered.connect(self.searchAction_)
        self.quit.triggered.connect(self.close)
        self.aboutQt.triggered.connect(self.aboutQt_)
        self.aboutApp.triggered.connect(self.aboutApp_)
        
        self.passAction.triggered.connect(self.passAction_)
        self.estimateAction.triggered.connect(self.estimateAction_)
        
        self.styleGroup.triggered.connect(self.changeBoardStyle)
        self.withCoordinate.toggled.connect(self.withCoordinate_)
        
        self.stepNumberAll.triggered.connect(self.board.update)
        self.stepNumberCurrent.triggered.connect(self.board.update)
        
        self.musicAction.toggled.connect(self.startMusic)
        
    def setUi(self):        
        self.menuBar = QMenuBar(self)
        
        gameMenu = self.menuBar.addMenu(_("Game"))
        self.newGame = QAction(_("New"))
        self.fileOpen = QAction(_("Open..."))
        self.ai = QAction(_("AI mode (gnugo)"))
        gameMenu.addAction(self.newGame)
        gameMenu.addAction(self.fileOpen)
        gameMenu.addAction(self.ai)
        gameMenu.addSeparator()
        self.printGo = QAction(_("Print..."))
        self.printGoPreview = QAction(_("Preview..."))
        gameMenu.addAction(self.printGo)
        gameMenu.addAction(self.printGoPreview)
        gameMenu.addSeparator()
        self.quit = QAction(_("Quit"))
        gameMenu.addAction(self.quit)
        
        displayMenu = self.menuBar.addMenu(_("Display"))
        
        self.withCoordinate = QAction(_("Coordinate"))
        self.withCoordinate.setCheckable(True)
        self.withCoordinate.setChecked(self.coordinate)
        displayMenu.addAction(self.withCoordinate)
        
        stepNumberMenu = displayMenu.addMenu(_("Step number"))
        self.stepNumberGroup = QActionGroup(self)
        self.stepNumberAll = QAction(_("All"))
        self.stepNumberAll.setCheckable(True)
        self.stepNumberCurrent = QAction(_("Current"))
        self.stepNumberCurrent.setCheckable(True)
        self.stepNumberHide = QAction(_("Hide"))
        self.stepNumberHide.setCheckable(True)
        self.stepNumberGroup.addAction(self.stepNumberAll)
        self.stepNumberGroup.addAction(self.stepNumberCurrent)
        self.stepNumberGroup.addAction(self.stepNumberHide)
        if self.stepNumber == "all":
            self.stepNumberAll.setChecked(True)
        elif self.stepNumber == "current":
            self.stepNumberCurrent.setChecked(True)
        else:
            self.stepNumberHide.setChecked(True)
        stepNumberMenu.addAction(self.stepNumberAll)
        stepNumberMenu.addAction(self.stepNumberCurrent)
        stepNumberMenu.addSeparator()
        stepNumberMenu.addAction(self.stepNumberHide)
        
        boardStyleMenu = displayMenu.addMenu(_("Board style"))
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
        
        soundMenu = self.menuBar.addMenu(_("Sound"))
        self.musicAction = QAction(_("Music"))
        self.musicAction.setCheckable(True)
        self.musicAction.setChecked(self.music)
        if not self.musicPath:
            self.musicAction.setEnabled(False)
        self.soundEffect = QAction(_("Sound Effect"))
        self.soundEffect.setCheckable(True)
        self.soundEffect.setChecked(self.effect)
        soundMenu.addAction(self.musicAction)
        soundMenu.addAction(self.soundEffect)
        
        websgfMenu = self.menuBar.addMenu(_("Web sgf"))
        self.foxAction = QAction(_("Download from Tx Weiqi..."))
        self.sinaAction = QAction(_("Download from Sina Weiqi..."))
        self.cyberoroAction = QAction(_("Download from Cyberoro..."))
        self.searchAction = QAction(_("Search local sgf..."))
        websgfMenu.addAction(self.foxAction)
        websgfMenu.addAction(self.sinaAction)
        websgfMenu.addAction(self.cyberoroAction)
        websgfMenu.addSeparator()
        websgfMenu.addAction(self.searchAction)
        
        settingMenu = self.menuBar.addMenu(_("Configration"))
        self.settingAction = QAction(_("Configrate foxGo..."))
        settingMenu.addAction(self.settingAction)
        
        helpMenu = self.menuBar.addMenu(_("Help"))
        self.aboutApp = QAction(_("About foxGo..."))
        self.aboutQt = QAction(_("About Qt..."))
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
        self.backToPoint = QPushButton(_("Back"), self)
        self.backToPoint.setEnabled(False)
        self.stepsSlider = QSlider(self)
        self.stepsSlider.setTracking(True)
        self.stepsSlider.setOrientation(Qt.Horizontal)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.stepsSlider.setSizePolicy(sizePolicy)
        
        self.otherButton = QPushButton(_("Ai mode options"), self)
        self.otherButton.setEnabled(False)
        otherMenu = QMenu(self)
        self.passAction = QAction(_("Pass"), self)
        #self.resignAction = QAction(_(("Resign"), self)
        self.replayAction = QAction(_("Replay"), self)
        self.estimateAction = QAction(_("Estimate"), self)
        self.quitAction = QAction(_("Quit"), self)
        otherMenu.addAction(self.passAction)
        #otherMenu.addAction(self.resignAction)
        otherMenu.addAction(self.replayAction)
        otherMenu.addAction(self.estimateAction)
        otherMenu.addAction(self.quitAction)
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
        vlayout.setContentsMargins(30, 30, 0, 30)
        self.playerLabel = QLabel(self)
        font1 = self.playerLabel.font()
        font1.setBold(True)
        font1.setPointSize(20)
        self.playerLabel.setFont(font1)
        self.gameInfo = QLabel(self)
        font2 = self.gameInfo.font()
        font2.setPointSize(10)
        self.gameInfo.setFont(font2)
        
        self.commentLabel = QLabel(_("Comments"), self)
        self.commentBox = QTextBrowser(self)
        self.commentBox.setOpenLinks(False)
        vlayout.addWidget(self.playerLabel)
        vlayout.addWidget(self.gameInfo)
        vlayout.addWidget(self.commentLabel)
        vlayout.addWidget(self.commentBox)
        
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
        self.coordLabel = QLabel("application coordinate: %d,%d      board coordinate: %d,%d      go coordinate: %d,%d", self)
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
            self.otherButton.setEnabled(True)
            self.stepPoint = 0
            self.breakPoint = 0
            self.showStepsCount(True)
            self.modeLabel.setText(_("Current mode: AI"))
            self.thisGame = goEngine.go()
            self.board.update()
            self.waitAi = getOutputThread(self)
            self.waitAi.trigger.connect(self.aiMessage)
            self.goSocket = aiDialog.goSocket
            self.process = aiDialog.process
            if aiDialog.blackStone.isChecked():
                self.peopleColor = "black"
                self.aiColor = "white"
            else:
                self.peopleColor = "white"
                self.aiColor = "black"
                self.communicateAi("genmove") # args = clear_board, final_score, genmove, play, pass, resign, quit
            
    
    def communicateAi(self, m):
        if m == "genmove":
            self.waitAi.command = "genmove {0}\n".format(self.aiColor)
            self.waitAi.run()
        elif m == "play":
            t = self.toGtpCoordinate(self.thisGame.x, self.thisGame.y)
            self.waitAi.command = "play {0} {1}\n".format(self.peopleColor, t)
            self.waitAi.run()
        elif m == "pass":
            self.thisGame.changeColor()
            self.waitAi.command = "play {0} pass\n".format(self.peopleColor)
            self.waitAi.run()
        elif m == "quit":
            self.goSocket.close()
            self.process.communicate("quit\n")
            self.newGame_()
        elif m == "clear_board":
            self.waitAi.command = "clear_board\n"
            self.waitAi.run()
        elif m == "final_score":
            self.waitAi.command = "final_score\n"
            self.waitAi.run()
        
    def aiMessage(self, message):
        print(message)
        if message.lower() == "pass":
            self.thisGame.changeColor()
        elif message.lower() == "resign":
            QMessageBox.information(self, _("Game result"), _("Congratulations, you win this game!"))
        elif message == "":
            self.communicateAi("genmove")
        elif "+" in message:
            print(message)
            c, score = message.split("+")
            if c == "B":
                p = _("Black")
            else:
                p = _("White")
            final = p + _("leads") + score
            QMessageBox.information(self, _("Game situation"), final)
        else:
            self.thisGame.x, self.thisGame.y = self.fromGtpCoordinate(message)
            print("AI move: {0},{1}".format(self.thisGame.x, self.thisGame.y))
            moveSuccess , deadChessNum = self.thisGame.makeStep()
            self.stepPoint += 1
            self.showStepsCount(True)
            self.board.update()
            self.makeSound(moveSuccess, deadChessNum)
            #self.thisGame.changeColor()
        
    
    def startFreeMode(self):
        self.mode = "free"
        self.commentBox.clear()
        self.stepPoint = 0
        self.breakPoint = 0
        self.thisGame = goEngine.go()
        self.showStepsCount(True)
        self.modeLabel.setText(_("Current mode: free"))
        self.otherButton.setEnabled(False)
    
    def restartFreeAndTestMode(self):
        self.thisGame.stepsGo = self.thisGame.stepsGo[:self.stepPoint]
        self.reviewMove()
    
    def startTestMode(self, vl = []):
        self.mode = "test"
        self.commentBox.clear()
        self.modeLabel.setText(_("Current mode: test"))
        self.breakPoint = self.stepPoint
        self.stepsGo_original = list(self.thisGame.stepsGo)
        #self.clearLength = len(self.thisGame.stepsGoDict)
        self.thisGame.stepsGo = self.thisGame.stepsGo[:self.stepPoint] + vl
        self.stepPoint += len(vl)
        #self.showStepsCount()
        self.reviewMove()
        self.backToPoint.setEnabled(True)
        self.otherButton.setEnabled(False)
        
    def startReviewMode(self, f):
        try:
            self.sgfEngine = sgfData.sgfData(f)
        except:
            QMessageBox.critical(self, _("Sfg file parse error"), _("It may be caused because of broken sfg file!"))
        else:
            self.mode = "review"
            self.commentBox.clear()
            self.otherButton.setEnabled(False)
            self.modeLabel.setText(_("Current mode: Review"))
        
            self.thisGame = goEngine.go()
            self.thisGame.stepsGo, self.thisGame.ha = self.sgfEngine.getStepsData(self.sgfEngine.rest)
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
        game = "{0} {1}\n\n".format(_("Game:"), self.sgfEngine.getTitle())
        date = "{0} {1}\n\n".format(_("Date:"), self.sgfEngine.getDate())
        komi = "{0} {1}\n\n".format(_("Komi:"), self.sgfEngine.getKomi())
        result = "{0} {1}\n\n".format(_("Result:"), self.sgfEngine.getResult())
        self.gameInfo.setText(game + date + komi + result)
    
    def getPlayersInfo(self):
        Pb = "{0} {1} {2}\n\n".format(_("Black:"), self.sgfEngine.getBlackPlayer(), self.sgfEngine.getBlackPlayerDan())
        Pw = "{0} {1} {2}\n\n".format(_("White:"), self.sgfEngine.getWhitePlayer(), self.sgfEngine.getWhitePlayerDan())
        self.playerLabel.setText(Pb+Pw)
    
    def initInfoLabel(self):
        self.gameInfo.setText("{0}  {4}\n\n{1}  {4}\n\n{2}  {4}\n\n{3}  {4}\n\n".format(_("Game:"), _("Date:"), _("Komi:"), _("Result:"), _("N/A")))
        self.playerLabel.setText("{0}  {2}\n\n{1}  {2}\n\n".format(_("Black:"), _("White:"), _("N/A")))
    
    def backToPoint_(self):
        self.mode = "review"
        self.commentBox.clear()
        self.modeLabel.setText(_("Current mode: Review"))
        self.thisGame.stepsGo = self.stepsGo_original
        self.stepPoint = self.breakPoint
        self.breakPoint = 0
        self.stepsCount.setMaximum(len(self.thisGame.stepsGo))
        self.stepsSlider.setMaximum(len(self.thisGame.stepsGo))
        self.showStepsCount()
        self.reviewMove()
        self.backToPoint.setEnabled(False)
    
    def getFile(self):
        fileName, y = QFileDialog.getOpenFileName(self, _("Open a SGF file"), self.sgfPath, _("Go records file(*.sgf)"))
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
    
    def passAction_(self):
        if self.mode == "free" or self.mode == "test":
            self.makeSound(1, 0)
            self.thisGame.changeColor()
        elif self.mode == "review":
            pass # real pass
        else:
            self.communicateAi("pass")
    
    def quitAction_(self):
        self.communicateAi("quit")
    
    def estimateAction_(self):
        self.communicateAi("final_score")
        
    
    def reviewMove(self):
        self.thisGame.stepsGoDict = {}
        
        for i in self.thisGame.ha:
            self.thisGame.stepsGoDict[i] = ("black", 0)
                
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
            url = "%d-%d" %(self.stepPoint, p)
            title = _("Variation: %s") %(url,)
            text += '<a href="%s">%s</a> %s<br>' %(url, title, co)
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
        self.stoneSound.setSource(QUrl.fromLocalFile(soundFile))
        self.stoneSound.play()
    
    def settingAction_(self):
        self.configDialog = configration()
        self.configDialog.path.lineEdit.setText(self.sgfPath)
        self.configDialog.music.musicBox.setText(self.musicPath)
        self.configDialog.download.autoSkip.setChecked(self.autoSkip)
        if self.saveAs:
            self.configDialog.download.saveAs.setChecked(True)
        else:
            self.configDialog.download.autoCover.setChecked(True)
        self.configDialog.gnugo.address.setText(self.address)
        self.configDialog.gnugo.port.setText(self.port)
        
        if self.configDialog.exec_() == QDialog.Accepted:
            self.sgfPath = self.configDialog.path.lineEdit.text()
            self.musicPath = self.configDialog.music.musicBox.text()
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
        
        if not self.musicPath:
            self.musicAction.setEnabled(False)
        else:
            self.musicAction.setEnabled(True)
    
    def startMusic(self, b):
        print("music")
        if b:
            self.backgroundMusic.play()
        else:
            self.backgroundMusic.stop()
    
    def foxAction_(self):
        self.tx = txwq(self)
        self.tx.show()
    
    def sinaAction_(self):
        self.sina = sinawq(self)
        self.sina.show()
    
    def cyberoroAction_(self):
        self.cyberoro = cyberoro(self)
        self.cyberoro.show()
    
    def searchAction_(self):
        self.searchBox = searchLocal(self)
        self.searchBox.show()
    
    def aboutQt_(self):
        QMessageBox.aboutQt(self, _("About Qt"))
    
    def aboutApp_(self):
        QMessageBox.about(self, _("About foxGo"), _("Enjoy Go's magic with foxGo under Linux environment"))
    
    def toGtpCoordinate(self, x, y):
        if x <= 8:
            xname = chr(x + 64)
        else:
            xname = chr(x + 65)
        yname = str(20 - y)
        gtp = xname + yname
        return gtp
    
    def fromGtpCoordinate(self, c):
        xname = c[0]
        yname = c[1:]
        xname_ = ord(xname)
        if xname_ <= 72:
            x = int(xname_ - 64)
        else:
            x = int(xname_ - 65)
        y = 20 - int(yname)
        return x, y
    
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
        if self.stepNumberAll.isChecked():
            cf.set("Board", "stepnumber", "all")
        elif self.stepNumberCurrent.isChecked():
            cf.set("Board", "stepnumber", "current")
        else:
            cf.set("Board", "stepnumber", "hide")
        if self.boardStyle1.isChecked():
            cf.set("Board", "style", "style1")
        elif self.boardStyle2.isChecked():
            cf.set("Board", "style", "style2")
        if self.withCoordinate.isChecked():
            cf.set("Board", "coordinate", "True")
        else:
            cf.set("Board", "coordinate", "False")
        cf.set("Sound", "musicpath", self.musicPath)
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
