#! /usr/bin/python


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, os
import glob
from configparser import ConfigParser


class myToolbar(QToolBar):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setOrientation(Qt.Vertical)
        self.myMenu = QMenu()
        self.addLabel = QAction("Add label", self)
        self.delLabel = QAction("Del label", self)
        self.myMenu.addAction(self.addLabel)
        self.myMenu.addAction(self.delLabel)
        
        
    def contextMenuEvent(self,ev):
        self.myMenu.popup(ev.globalPos())
        


class searchLocal(QWidget):
    
    def __init__(self, parent = None):
        super().__init__()
        
        cf = ConfigParser()
        cf.read(os.path.expanduser("~/.config/foxGo.conf"))
        m = cf.get("Tag", "tags").split(",")
        self.labelList = []
        for j in m:
            if j != "":
                self.labelList.append(j.strip())
        
        self.setWindowIcon(QIcon("res/logo.png"))
        self.setWindowTitle("Search local sgf files")
        self.resize(700, 500)
        self.parent = parent
        self.sgfPath = parent.sgfPath
        #self.sgfPath = "/home/frank/Downloads/sgf"
        
        h1 = QHBoxLayout(None)
        h1.setContentsMargins(20, 0, 0, 0)
        self.rangeLabel = QLabel("Select range:", self)
        self.rangeCombo = QComboBox(self)
        d = ["All"]
        for i in glob.glob(os.path.join(self.sgfPath, "*")):
            if os.path.isdir(i):
                d.append(os.path.split(i)[-1])
        self.rangeCombo.addItems(d)
        self.dirList = d[1:]
        
        self.searchLabel = QLabel("Search:", self)
        self.searchBox = QLineEdit(self)
        self.searchBox.setClearButtonEnabled(True)
        h1.addWidget(self.rangeLabel)
        h1.addWidget(self.rangeCombo)
        h1.addSpacing(80)
        h1.addWidget(self.searchLabel)
        h1.addWidget(self.searchBox)
        
        self.listView = QTableWidget(0, 1, self)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.listView.setSelectionMode(QAbstractItemView.SingleSelection)
        header = ["Title", "From"]
        self.listView.setHorizontalHeaderLabels(header)
        #self.listView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.listView.horizontalHeader().resizeSection(0, 530)
        
        h2 = QVBoxLayout(None)
        h2.addLayout(h1)
        h2.addWidget(self.listView)
        
        h3 = QVBoxLayout(None)
        h3.setContentsMargins(0, 7, 0, 0)
        self.quickLabel = QLabel("Search Label", self)
        self.quickLabel.setAlignment(Qt.AlignCenter)
        self.quickSearch = myToolbar(self)
        self.quickSearch.setOrientation(Qt.Vertical)
        self.showLabel()
        h3.addWidget(self.quickLabel, 0)
        h3.addWidget(self.quickSearch, 1)
        
        h4 = QHBoxLayout(None)
        h4.addLayout(h3)
        h4.addLayout(h2)
        
        h5 = QHBoxLayout(None)
        self.openButton = QPushButton("Open", self)
        self.quitButton = QPushButton("Quit", self)
        h5.addStretch(10)
        h5.addWidget(self.openButton,1)
        h5.addWidget(self.quitButton,1)
        
        mainLayout = QVBoxLayout(None)
        mainLayout.addLayout(h4)
        #mainLayout.addWidget(self.listView)
        mainLayout.addLayout(h5)
        self.setLayout(mainLayout)
        
        self.showSgfItems("All")
        
        self.quitButton.clicked.connect(self.close)
        self.rangeCombo.currentTextChanged.connect(self.showSgfItems)
        self.searchBox.textChanged.connect(self.showSearchResult)
        self.openButton.clicked.connect(self.getFileName)
        self.listView.cellActivated.connect(self.enableOpenButton)
        self.listView.cellDoubleClicked.connect(self.doubleClickOpen)
        
        self.quickSearch.addLabel.triggered.connect(self.addLabel_)
        self.quickSearch.delLabel.triggered.connect(self.delLabel_)
        self.quickSearch.actionTriggered.connect(self.addWords)
    
    def addWords(self, action):
        self.searchBox.setText(action.text())
    
    def addLabel_(self):
        name, ok= QInputDialog.getText(self, "Add a label", "Key words of label:")
        if ok and name != "":
            self.labelList.append(name)
            self.showLabel()
    
    def delLabel_(self):
        name, ok = QInputDialog.getItem(self, "Del a label", "Please choose the label:", self.labelList, 0, False)
        if ok:
            self.labelList.remove(name)
            self.showLabel()
    
    def showLabel(self):
        self.quickSearch.clear()
        for i in self.labelList:
            self.quickSearch.addAction(QAction(i, self))
    
    def enableOpenButton(self, r, c):
        self.openButton.setEnabled(True)
    
    def doubleClickOpen(self, r, c):
        t = self.listView.item(r, c).text()
        ind = -1
        for i in self.titleList:
            ind += 1
            if t in i:
                break
        self.parent.startReviewMode(self.titleList[ind])
    
    def getFileName(self):
        t = self.listView.selectedItems()[0].text()
        ind = -1
        for i in self.titleList:
            ind += 1
            if t in i:
                break
        self.parent.startReviewMode(self.titleList[ind])
    
    def showSearchResult(self, t):
        self.openButton.setEnabled(False)
        #t = self.searchBox.text()
        self.listView.clearContents()
        tmpList = []
        for i in self.titleList:
            if t in i:
                tmpList.append(i)
        row = 0
        for j in tmpList:
            row += 1
            self.listView.setRowCount(row)
            n = os.path.split(j)[1]
            name = os.path.splitext(n)[0]
            self.listView.setItem(row-1, 0, QTableWidgetItem(name))
    
    def showSgfItems(self, t):
        self.openButton.setEnabled(False)
        self.searchBox.clear()
        self.listView.clearContents()
        self.titleList = []
        row = 0
        if t == "All":
            for i in self.dirList:
                path = os.path.join(self.sgfPath, i)
                #print(path)
                for j in glob.glob(os.path.join(path, "*.sgf")):
                    row += 1
                    self.listView.setRowCount(row)
                    self.titleList.append(j)
                    n = os.path.split(j)[1]
                    name = os.path.splitext(n)[0]
                    self.listView.setItem(row-1, 0, QTableWidgetItem(name))
        else:
            path = os.path.join(self.sgfPath, t)
            for j in glob.glob(os.path.join(path, "*.sgf")):
                row += 1
                self.listView.setRowCount(row)
                self.titleList.append(j)
                n = os.path.split(j)[1]
                name = os.path.splitext(n)[0]
                self.listView.setItem(row-1, 0, QTableWidgetItem(name))
                
    def closeEvent(self, e):
        tagString = ""
        for i in self.labelList:
            tagString += "{0}, ".format(i)
        cf = ConfigParser()
        cf.read(os.path.expanduser("~/.config/foxGo.conf"))
        cf.set("Tag", "tags", tagString)
        f = open(os.path.expanduser("~/.config/foxGo.conf"), 'w')
        cf.write(f)
        f.close()
        
        e.accept()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = searchLocal()
	w.show()
	sys.exit(app.exec_())
