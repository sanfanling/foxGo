#! /usr/bin/python

import sys
from PyQt5.QtCore import *


class getOutputThread(QThread):
    
    trigger = pyqtSignal(str)
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.command = None

    
    def run(self):
        self.parent.goSocket.sendall(self.command.encode("utf8"))
        result = ""
        while True:
            d = self.parent.goSocket.recv(1024 * 1024).decode("utf8")
            result += d
            if '\n\n' in d:
                break
        result = result.replace("=", "")    
        print("thread: {}".format(result.strip()))
        self.trigger.emit(result.strip())
        
        
        #if self.send:
            #self.peopleMove()
            
        #if self.receive:
            #message = self.aiMove()
            #if message.lower() == "pass":
                #pass
            #elif message.lower() == "resign":
                #pass
            #else:
                #self.parent.thisGame.x, self.parent.thisGame.y = self.fromGtpCoordinate(message)
        
        

class getCatalogThread(QThread):
    
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
    
    def run(self):
        catalogUrl = self.parent.parser.getCatalogUrl()
        page = self.parent.parser.getCatalog(catalogUrl)
        self.parent.pageList = self.parent.parser.parseCatalog(page)
