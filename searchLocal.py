#! /usr/bin/python


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys, os
import glob


class searchLocal(QWidget):
    
    def __init__(self, parent = None):
        super().__init__()
        
        self.setWindowIcon(QIcon("res/logo.png"))
        self.setWindowTitle("Search local sgf files")
        self.resize(600, 500)
        self.parent = parent
        self.sgfPath = parent.sgfPath
        #self.sgfPath = "/home/frank/Downloads/sgf"
        
        h1 = QHBoxLayout(None)
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
        
        h2 = QHBoxLayout(None)
        self.openButton = QPushButton("Open", self)
        self.quitButton = QPushButton("Quit", self)
        h2.addStretch(10)
        h2.addWidget(self.openButton,1)
        h2.addWidget(self.quitButton,1)
        
        mainLayout = QVBoxLayout(None)
        mainLayout.addLayout(h1)
        mainLayout.addWidget(self.listView)
        mainLayout.addLayout(h2)
        self.setLayout(mainLayout)
        
        self.showSgfItems("All")
        
        self.quitButton.clicked.connect(self.close)
        self.rangeCombo.currentTextChanged.connect(self.showSgfItems)
        self.searchBox.textChanged.connect(self.showSearchResult)
        self.openButton.clicked.connect(self.getFileName)
        self.listView.cellActivated.connect(self.enableOpenButton)
        self.listView.cellDoubleClicked.connect(self.doubleClickOpen)
    
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

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = searchLocal()
	w.show()
	sys.exit(app.exec_())
