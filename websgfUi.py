#!/bin/use/python

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class websgfUi(QWidget):
    
    def __init__(self, parent = None):
        super().__init__()
        
        self.listView = QTableWidget(0, 4, self)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.listView.setSelectionMode(QAbstractItemView.SingleSelection)
        header = [self._("Select"), self._("Game"), self._("Result"), self._("Date")]
        self.listView.setHorizontalHeaderLabels(header)
        #self.listView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        
        hlayout_1 = QHBoxLayout(None)
        self.previous10Page = QPushButton(self._("Previous 10 page"), self)
        self.previousPage = QPushButton(self._("Previous page"), self)
        self.pageLabel = QLabel(self._("Go to page:"), self)
        self.pageLabel.setAlignment(Qt.AlignRight)
        self.pageNum = QSpinBox(self)
        self.nextPage = QPushButton(self._("Next page"), self)
        self.next10Page = QPushButton(self._("Next 10 page"), self)
        hlayout_1.addWidget(self.previous10Page)
        hlayout_1.addWidget(self.previousPage)
        hlayout_1.addWidget(self.pageLabel)
        hlayout_1.addWidget(self.pageNum)
        hlayout_1.addWidget(self.nextPage)
        hlayout_1.addWidget(self.next10Page)
        
        hlayout_2 = QHBoxLayout(None)
        self.downloadButton = QPushButton(self._("Downlaod"), self)
        self.quitButton = QPushButton(self._("Quit"), self)
        hlayout_2.addWidget(self.downloadButton)
        hlayout_2.addWidget(self.quitButton)
        hlayout_2.setContentsMargins(400, 0, 0, 0)
        
        mainLayout = QVBoxLayout(None)
        mainLayout.addWidget(self.listView)
        mainLayout.addLayout(hlayout_1)
        mainLayout.addLayout(hlayout_2)
        self.setLayout(mainLayout)
        
        self.quitButton.clicked.connect(self.close)
    
    def _(self, s):
        return QCoreApplication.translate('websgfUi', s)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = websgfUi()
	w.show()
	sys.exit(app.exec_())
