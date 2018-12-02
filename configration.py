#! /usr/bin/python



from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from configparser import ConfigParser
import os, sys


class configration(QDialog):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Configrate foxGo"))
        self.setWindowIcon(QIcon("res/icon.png"))
        
        self.path = path(self)
        self.download = download(self)
        self.gnugo = gnugo(self)
        
        self.buttonBox = QDialogButtonBox(self)
        okButton = QPushButton(self.tr("OK"))
        cancelButton = QPushButton(self.tr("Cancel"))
        self.buttonBox.addButton(okButton, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(cancelButton, QDialogButtonBox.RejectRole)
        
        mainLayout = QVBoxLayout(None)
        mainLayout.addWidget(self.path)
        mainLayout.addWidget(self.download)
        mainLayout.addWidget(self.gnugo)
        mainLayout.addSpacing(30)
        mainLayout.addWidget(self.buttonBox)
        
        self.setLayout(mainLayout)
        
        
        
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        

class path(QFrame):
    
    def __init__(self, parent):
        super().__init__()
        self.setFrameShape(QFrame.Box)
        v1 = QVBoxLayout(None)
        self.pathLabel = QLabel(self.tr("Sgf path"), self)
        self.pathLabel.setAlignment(Qt.AlignCenter)
        
        h1 = QHBoxLayout(None)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setReadOnly(True)
        self.choosePath = QPushButton(self.tr("Choose..."))
        h1.addWidget(self.lineEdit)
        h1.addWidget(self.choosePath)
        
        v1.addWidget(self.pathLabel)
        v1.addLayout(h1)
        v1.addStretch(10)
        
        self.setLayout(v1)
    
        self.choosePath.clicked.connect(self.choosePath_)
    
    def choosePath_(self):
        directory = QFileDialog.getExistingDirectory(self, self.tr("Choose a directory to save SGF files"), os.path.expanduser("~"), QFileDialog.ShowDirsOnly)
        if directory:
            self.lineEdit.setText(directory)

class download(QFrame):
    
    def __init__(self, parent):
        super().__init__()
        self.setFrameShape(QFrame.Box)
        v1 = QVBoxLayout(None)
        self.downloadLabel = QLabel(self.tr("Download"), self)
        self.downloadLabel.setAlignment(Qt.AlignCenter)
        
        h1 = QVBoxLayout(None)
        self.autoSkip = QCheckBox(self.tr("Auto skip if the sgf file exists already"), self)
        self.saveAs = QRadioButton(self.tr("Ask user to saveas the existed sgf files"), self)
        self.autoCover = QRadioButton(self.tr("Auto cover the existed sgf files"), self)
        h1.addWidget(self.autoSkip)
        h1.addWidget(self.saveAs)
        h1.addWidget(self.autoCover)
        
        v1.addWidget(self.downloadLabel)
        v1.addLayout(h1)
        v1.addStretch(10)
        
        self.setLayout(v1)
        
        self.autoSkip.toggled.connect(self.saveAs.setDisabled)
        self.autoSkip.toggled.connect(self.autoCover.setDisabled)
        
class gnugo(QFrame):
    
    def __init__(self, parent):
        super().__init__()
        self.setFrameShape(QFrame.Box)
        v1 = QVBoxLayout(None)
        self.gnugoLabel = QLabel(self.tr("Gnugo"), self)
        self.gnugoLabel.setAlignment(Qt.AlignCenter)
        
        h1 = QHBoxLayout(None)
        self.addressLabel = QLabel(self.tr("Server address:"), self)
        self.address = QLineEdit(self)
        self.address.setAlignment(Qt.AlignCenter)
        self.address.setInputMask("000.000.000.000;_")
        h1.addWidget(self.addressLabel, 1)
        h1.addWidget(self.address, 1)
        
        h2 = QHBoxLayout(None)
        self.portLabel = QLabel(self.tr("Server port:"), self)
        self.port = QLineEdit(self)
        self.port.setAlignment(Qt.AlignRight)
        h2.addWidget(self.portLabel, 4)
        h2.addWidget(self.port, 1)
        
        self.infoLabel = QLabel(self.tr("*This setting will take effect in next Ai mode startup"), self)
        
        v1.addWidget(self.gnugoLabel)
        v1.addLayout(h1)
        v1.addLayout(h2)
        v1.addWidget(self.infoLabel)
        v1.addStretch(10)
        
        self.setLayout(v1)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = configration()
	w.show()
	sys.exit(app.exec_())
