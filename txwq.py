#! /usr/bin/python

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from websgfUi import websgfUi
from websgf.txwqSgfParser import txwqSgfParser
import sys, os


class txwq(websgfUi):
    
    def __init__(self, parent = None):
        super().__init__()
        self.resize(800, 500)
        self.basePath = parent.sgfPath
        self.extensionPath = "txwq"
        targetDir = os.path.join(self.basePath, self.extensionPath)
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        self.parser = txwqSgfParser()
        self.showPageNum()
        self.showContent()
        self.changeButtonStatus()
        self.pageNum.setRange(1, self.parser.pageLimited)
        
        self.pageNum.editingFinished.connect(self.gotoPage)
        self.nextPage.clicked.connect(self.gotoNextPage)
        self.previousPage.clicked.connect(self.gotoPreviousPage)
        self.next10Page.clicked.connect(self.gotoNext10Page)
        self.previous10Page.clicked.connect(self.gotoPrevious10Page)
        self.downloadButton.clicked.connect(self.download)
    
    def changeButtonStatus(self):
        if self.parser.pageLimited - self.parser.currentPage > 0:
            self.nextPage.setEnabled(True)
        else:
            self.nextPage.setEnabled(False)
        
        if self.parser.pageLimited - self.parser.currentPage >= 10:
            self.next10Page.setEnabled(True)
        else:
            self.next10Page.setEnabled(False)
            
        if self.parser.currentPage - 1 > 0:
            self.previousPage.setEnabled(True)
        else:
            self.previousPage.setEnabled(False)
        
        if self.parser.currentPage - 10 > 0:
            self.previous10Page.setEnabled(True)
        else:
            self.previous10Page.setEnabled(False)
    
    def gotoNextPage(self):
        self.parser.currentPage += 1
        self.showPageNum()
        self.showContent()
        self.changeButtonStatus()
    
    def gotoPreviousPage(self):
        self.parser.currentPage -= 1
        self.showPageNum()
        self.showContent()
        self.changeButtonStatus()
    
    def gotoNext10Page(self):
        self.parser.currentPage += 10
        self.showPageNum()
        self.showContent()
        self.changeButtonStatus()
    
    def gotoPrevious10Page(self):
        self.parser.currentPage -= 10
        self.showPageNum()
        self.showContent()
        self.changeButtonStatus()
    
    def gotoPage(self):
        self.parser.currentPage = self.pageNum.value()
        self.showContent()
        self.changeButtonStatus()
    
    def showPageNum(self):
        self.pageNum.setValue(self.parser.currentPage)
        
    def showContent(self):
        self.pageList = []
        catalogUrl = self.parser.getCatalogUrl()
        page = self.parser.getCatalog(catalogUrl)
        self.pageList = self.parser.parseCatalog(page)
        
        row = 0
        for url, game, res, date in self.pageList:
            row += 1            
            self.listView.setRowCount(row)
            self.listView.setCellWidget(row-1, 0, QCheckBox())
            self.listView.setItem(row-1, 1, QTableWidgetItem(game))
            self.listView.setItem(row-1, 2, QTableWidgetItem(res))
            self.listView.setItem(row-1, 3, QTableWidgetItem(date))
    
    def getDownloadList(self):
        downloadList = []
        for i in range(self.listView.rowCount()):
            widget = self.listView.cellWidget(i, 0)
            if widget.isChecked():
                downloadList.append(i)
        return downloadList
    
    def download(self):
        for i in self.getDownloadList():
            gameName = self.pageList[i][1]
            resName = self.pageList[i][2]
            name = "%s-%s.sgf" %(gameName, resName)
            name = name.replace("/", "-")
            
            fileName = os.path.join(self.basePath, self.extensionPath, name)
            if os.path.exists(fileName):
                continue
            else:
                sgf = self.parser.getSgf(self.pageList[i][0])
                f = open(fileName, "w")
                f.write(sgf)
                f.close()
        b = QMessageBox(self)
        b. setText("Success downloading!")
        b.exec_()
        
if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = txwq()
	w.show()
	sys.exit(app.exec_())
