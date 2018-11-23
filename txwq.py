#! /usr/bin/python

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from websgfUi import websgfUi
from websgf.txwqSgfParser import txwqSgfParser
from myThread import getCatalogThread
import sys, os


class txwq(websgfUi):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setWindowIcon(QIcon("res/logo.png"))
        self.setWindowTitle("Download sgf files from tx weiqi")
        self.listView.horizontalHeader().resizeSection(0, 50)
        self.listView.horizontalHeader().resizeSection(1, 360)
        self.listView.horizontalHeader().resizeSection(2, 200)
        self.listView.horizontalHeader().resizeSection(3, 120)
        self.resize(800, 500)
        self.autoSkip = parent.autoSkip
        self.saveAs = parent.saveAs
        self.basePath = parent.sgfPath
        #self.basePath = "/home/frank/Downloads/sgf"
        self.extensionPath = "txwq"
        targetDir = os.path.join(self.basePath, self.extensionPath)
        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)
        self.parser = txwqSgfParser()
        self.showPageNum()
        self.contentThread = getCatalogThread(self)
        self.contentThread.start()
        
        
        self.pageNum.editingFinished.connect(self.gotoPage)
        self.nextPage.clicked.connect(self.gotoNextPage)
        self.previousPage.clicked.connect(self.gotoPreviousPage)
        self.next10Page.clicked.connect(self.gotoNext10Page)
        self.previous10Page.clicked.connect(self.gotoPrevious10Page)
        self.downloadButton.clicked.connect(self.download)
        self.contentThread.finished.connect(self.showContent)
    
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
        self.contentThread.start()
    
    def gotoPreviousPage(self):
        self.parser.currentPage -= 1
        self.showPageNum()
        self.contentThread.start()
    
    def gotoNext10Page(self):
        self.parser.currentPage += 10
        self.showPageNum()
        self.contentThread.start()
    
    def gotoPrevious10Page(self):
        self.parser.currentPage -= 10
        self.showPageNum()
        self.contentThread.start()
    
    def gotoPage(self):
        self.parser.currentPage = self.pageNum.value()
        self.contentThread.start()
    
    def showPageNum(self):
        self.pageNum.setValue(self.parser.currentPage)
        
        
    def showContent(self):
        self.pageNum.setRange(1, self.parser.pageLimited)
        row = 0
        for url, game, res, date in self.pageList:
            row += 1            
            self.listView.setRowCount(row)
            self.listView.setCellWidget(row-1, 0, QCheckBox())
            self.listView.setItem(row-1, 1, QTableWidgetItem(game))
            self.listView.setItem(row-1, 2, QTableWidgetItem(res))
            self.listView.setItem(row-1, 3, QTableWidgetItem(date))
        self.changeButtonStatus()
    
    def getDownloadList(self):
        downloadList = []
        for i in range(self.listView.rowCount()):
            widget = self.listView.cellWidget(i, 0)
            if widget.isChecked():
                downloadList.append(i)
        return downloadList
    
    def download(self):
        if len(self.getDownloadList()) == 0:
            b = QMessageBox(self)
            b. setText("No items selected!")
            b.exec_()
        else:
            for i in self.getDownloadList():
                gameName = self.pageList[i][1]
                resName = self.pageList[i][2]
                name = "%s-%s.sgf" %(gameName, resName)
                name = name.replace("/", "-")
            
                fileName = os.path.join(self.basePath, self.extensionPath, name)
                if os.path.exists(fileName) and self.autoSkip:
                    continue
                elif os.path.exists(fileName) and not self.autoSkip:
                    if self.saveAs:
                        re = QFileDialog.getSaveFileName(self, "Save as", fileName, "Go records file(*.sgf)")
                        tmpfile = re[0]
                        if tmpfile == "":
                            continue
                        else:
                            sgf = self.parser.getSgf(self.pageList[i][0])
                            f = open(tmpfile, "w")
                            f.write(sgf)
                            f.close()
                    else:
                        sgf = self.parser.getSgf(self.pageList[i][0])
                        f = open(fileName, "w")
                        f.write(sgf)
                        f.close()
                        
                else:
                    sgf = self.parser.getSgf(self.pageList[i][0])
                    f = open(fileName, "w")
                    f.write(sgf)
                    f.close()
            b = QMessageBox(self)
            b. setText("Download mission finished!")
            b.exec_()
        
if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = txwq()
	w.show()
	sys.exit(app.exec_())
