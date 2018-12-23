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
        self.addLabel = QAction(_("Add label"), self)
        self.delLabel = QAction(_("Del label"), self)
        self.myMenu.addAction(self.addLabel)
        self.myMenu.addAction(self.delLabel)
        
    def contextMenuEvent(self,ev):
        self.myMenu.popup(ev.globalPos())


class tagArea(QWidget):
    
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        h3 = QVBoxLayout(None)
        h3.setContentsMargins(0, 7, 0, 0)
        self.quickLabel = QLabel(_("Search Label"), self)
        self.quickLabel.setAlignment(Qt.AlignCenter)
        self.quickSearch = myToolbar(self)
        self.quickSearch.setOrientation(Qt.Vertical)
        #self.showLabel()
        h3.addWidget(self.quickLabel, 0)
        h3.addWidget(self.quickSearch, 1)
        
        self.setLayout(h3)
        
        
class searchArea(QWidget):
    
    def __init__(self, parent = None):
        super().__init__()
        
        self.parent = parent        
        h1 = QHBoxLayout(None)
        h1.setContentsMargins(20, 0, 0, 0)
        self.rangeLabel = QLabel(_("Select range:"), self)
        self.rangeCombo = QComboBox(self)
        d = [_("All")]
        for i in glob.glob(os.path.join(self.parent.sgfPath, "*")):
            if os.path.isdir(i):
                d.append(os.path.split(i)[-1])
        self.rangeCombo.addItems(d)
        self.dirList = d[1:]
        
        self.searchLabel = QLabel(_("Search:"), self)
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
        header = [_("Title"), _("From")]
        self.listView.setHorizontalHeaderLabels(header)
        #self.listView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.listView.horizontalHeader().resizeSection(0, 550)
        
        h2 = QVBoxLayout(None)
        h2.addLayout(h1)
        h2.addWidget(self.listView)
        self.setLayout(h2)
        

class searchLocal(QWidget):
    
    def __init__(self, parent = None):
        super().__init__()
        
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        cf = ConfigParser()
        cf.read(os.path.expanduser("~/.config/foxGo.conf"))
        m = cf.get("Tag", "tags").split(",")
        self.labelList = []
        for j in m:
            if j != "":
                self.labelList.append(j.strip())
        
        self.setWindowIcon(QIcon("res/logo.png"))
        self.setWindowTitle(_("Search local sgf files"))
        self.resize(730, 500)
        self.parent = parent
        self.sgfPath = parent.sgfPath
        #self.sgfPath = "/home/frank/Downloads/sgf"
        
        self.searchArea = searchArea(self)
        self.tagArea = tagArea(self)
        self.showLabel()
        splitter = QSplitter()
        splitter.addWidget(self.tagArea)
        splitter.addWidget(self.searchArea)
        
        
        h5 = QHBoxLayout(None)
        self.openButton = QPushButton(_("Open"), self)
        self.quitButton = QPushButton(_("Quit"), self)
        h5.addStretch(10)
        h5.addWidget(self.openButton,1)
        h5.addWidget(self.quitButton,1)
        
        mainLayout = QVBoxLayout(None)
        mainLayout.addWidget(splitter)
        mainLayout.addLayout(h5)
        
        self.setLayout(mainLayout)
        
        self.showSgfItems(_("All"))
        
        self.quitButton.clicked.connect(self.close)
        self.searchArea.rangeCombo.currentTextChanged.connect(self.showSgfItems)
        self.searchArea.searchBox.textChanged.connect(self.showSearchResult)
        self.openButton.clicked.connect(self.getFileName)
        self.searchArea.listView.cellActivated.connect(self.enableOpenButton)
        self.searchArea.listView.cellDoubleClicked.connect(self.doubleClickOpen)
        
        self.tagArea.quickSearch.addLabel.triggered.connect(self.addLabel_)
        self.tagArea.quickSearch.delLabel.triggered.connect(self.delLabel_)
        self.tagArea.quickSearch.actionTriggered.connect(self.addWords)
    
    def addWords(self, action):
        self.searchArea.searchBox.setText(action.text())
    
    def addLabel_(self):
        name, ok= QInputDialog.getText(self, _("Add a label"), _("Key words of label:"))
        if ok and name != "":
            self.labelList.append(name)
            self.showLabel()
    
    def showLabel(self):
        self.tagArea.quickSearch.clear()
        for i in self.labelList:
            self.tagArea.quickSearch.addAction(QAction(i, self))
            
    def delLabel_(self):
        name, ok = QInputDialog.getItem(self, _("Del a label"), _("Please choose the label:"), self.labelList, 0, False)
        if ok:
            self.labelList.remove(name)
            self.showLabel()
 
    def enableOpenButton(self, r, c):
        self.openButton.setEnabled(True)
    
    def doubleClickOpen(self, r, c):
        t = self.searchArea.listView.item(r, c).text()
        ind = -1
        for i in self.titleList:
            ind += 1
            if t in i:
                break
        self.parent.startReviewMode(self.titleList[ind])
        self.lower()
    
    def getFileName(self):
        t = self.searchArea.listView.selectedItems()[0].text()
        ind = -1
        for i in self.titleList:
            ind += 1
            if t in i:
                break
        self.parent.startReviewMode(self.titleList[ind])
        self.lower()
    
    def showSearchResult(self, t):
        self.openButton.setEnabled(False)
        #t = self.searchBox.text()
        self.searchArea.listView.clearContents()
        tmpList = []
        for i in self.titleList:
            if t in i:
                tmpList.append(i)
        row = 0
        for j in tmpList:
            row += 1
            self.searchArea.listView.setRowCount(row)
            n = os.path.split(j)[1]
            name = os.path.splitext(n)[0]
            self.searchArea.listView.setItem(row-1, 0, QTableWidgetItem(name))
    
    def showSgfItems(self, t):
        self.openButton.setEnabled(False)
        self.searchArea.searchBox.clear()
        self.searchArea.listView.clearContents()
        self.titleList = []
        row = 0
        if t == _("All"):
            for i in self.searchArea.dirList:
                path = os.path.join(self.sgfPath, i)
                #print(path)
                for j in glob.glob(os.path.join(path, "*.sgf")):
                    row += 1
                    self.searchArea.listView.setRowCount(row)
                    self.titleList.append(j)
                    n = os.path.split(j)[1]
                    name = os.path.splitext(n)[0]
                    self.searchArea.listView.setItem(row-1, 0, QTableWidgetItem(name))
        else:
            path = os.path.join(self.sgfPath, t)
            for j in glob.glob(os.path.join(path, "*.sgf")):
                row += 1
                self.searchArea.listView.setRowCount(row)
                self.titleList.append(j)
                n = os.path.split(j)[1]
                name = os.path.splitext(n)[0]
                self.searchArea.listView.setItem(row-1, 0, QTableWidgetItem(name))
                
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
