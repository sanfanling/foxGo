#! /usr/bin/python


from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimeLine
import subprocess
import sys, socket


class startAiDialog(QDialog):
    
    def __init__(self, parent = None):
        super().__init__()
        self.timer = QTimeLine(2000, self)
        #self.address = parent.address
        #self.port = parent.port
        self.address = "127.0.0.1"
        self.port = "5577"
        
        h1 = QHBoxLayout(None)
        self.yourLabel = QLabel(_("Your color:"), self)
        self.blackStone = QRadioButton(_("Black"), self)
        self.blackStone.setChecked(True)
        self.whiteStone = QRadioButton(_("White"), self)
        h1.addWidget(self.yourLabel)
        h1.addWidget(self.blackStone)
        h1.addWidget(self.whiteStone)
        
        h2 = QHBoxLayout(None)
        self.levelLabel = QLabel(_("Gnugo level:"), self)
        self.gnuLevel = QSpinBox(self)
        self.gnuLevel.setRange(1, 10)
        self.gnuLevel.setValue(8)
        h2.addWidget(self.levelLabel)
        h2.addWidget(self.gnuLevel)
        
        h3 = QHBoxLayout(None)
        self.komiLabel = QLabel(_("Set komi:"), self)
        self.komi = QSpinBox(self)
        self.komi.setEnabled(False)
        self.komi.setRange(0, 9)
        self.komi.setValue(0)
        h3.addWidget(self.komiLabel)
        h3.addWidget(self.komi)
        
        h4 = QHBoxLayout(None)
        self.startButton = QPushButton(_("Start Server"), self)
        buttonBox = QDialogButtonBox(self)
        self.okButton = QPushButton(_("OK"))
        self.okButton.setEnabled(False)
        self.cancelButton = QPushButton(_("Cancel"))
        buttonBox.addButton(self.okButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(self.cancelButton, QDialogButtonBox.RejectRole)
        h4.addWidget(self.startButton)
        h4.addWidget(buttonBox)
        
        mainLayout = QVBoxLayout(None)
        mainLayout.addLayout(h1)
        mainLayout.addLayout(h2)
        mainLayout.addLayout(h3)
        mainLayout.addLayout(h4)
        self.setLayout(mainLayout)
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.startButton.clicked.connect(self.startServer)
        self.timer.finished.connect(self.serverStarted)
    
    def serverStarted(self):
        self.goSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.goSocket.connect(("127.0.0.1", int(self.port)))
        self.startButton.setText(_("Server started"))
        self.okButton.setEnabled(True)
    
    def startServer(self):
        self.startButton.setEnabled(False)
        self.startButton.setText(_("Starting..."))
        if self.blackStone.isChecked():
            cl = "black"
        else:
            cl = "white"
        args = "gnugo --mode gtp --boardsize 19 --color {0} --level {1} --gtp-listen {2}:{3}".format(cl, str(self.gnuLevel.value()), self.address, self.port)
        print(args)
        self.process = subprocess.Popen(args.split())
        self.timer.start()
        


if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = startAiDialog()
	w.show()
	sys.exit(app.exec_())
