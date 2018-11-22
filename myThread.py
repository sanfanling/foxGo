#! /usr/bin/python

import sys
from PyQt5.QtCore import *


class getOutputThread(QThread):
    
    #trigger = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
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
    
    def run(self):
        #print("Black: %d,%d" %(self.parent.thisGame.x, self.parent.thisGame.y))
        gtp = self.toGtpCoordinate(self.parent.thisGame.x, self.parent.thisGame.y)
        data1 = "play black %s\n" %(gtp,)
        self.parent.goSocket.sendall(data1.encode("utf8"))
        
        while True:
            d = self.parent.goSocket.recv(1024 * 1024).decode("utf8")
            if '\n\n' in d:
                break
        
        data2 = "genmove white\n"
        self.parent.goSocket.sendall(data2.encode("utf8"))
        result = []
        while True:
            data3 = self.parent.goSocket.recv(1024 * 1024).decode("utf8")
            result.append(data3)
            if '\n\n' in data3:
                break
        result = ''.join(result)
        if result[0] == '?':
            raise FailedCommand(result)
        result = result[1:]
        data4 = result.strip().split(" ")[0]
        self.parent.thisGame.x, self.parent.thisGame.y = self.fromGtpCoordinate(data4)
        
        #self.trigger.emit()

class getCatalogThread(QThread):
    
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
    
    def run(self):
        catalogUrl = self.parent.parser.getCatalogUrl()
        page = self.parent.parser.getCatalog(catalogUrl)
        self.parent.pageList = self.parent.parser.parseCatalog(page)
