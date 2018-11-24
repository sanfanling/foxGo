#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: foxGo.py
# Develop CodeName: fox
# Version:  1.0.0
# Author: sanfanling
# Lisence: GPL-3.0
# Bug report: xujia19@outlook.com

#pyqtGo: Go application that aims to foxweiqi under linux environment with Qt library by python language
#Copyright (C) 2018 - 2019 Xu Jia <xujia19@outlook.com>

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from PyQt5.QtWidgets import QApplication
from mainWindow import mainWindow
import sys, os

# check the config file first

configContent = """
                [Path]
                sgfpath = ~
                
                [Download]
                autoskip = True
                saveas = False
                
                [Gnugo]
                address = 127.0.0.1
                port = 5522
                
                [Board]
                handcounts = False
                style = style1
                coordinate = False
                
                [Sound]
                music = False
                effect = False
		
		[Tag]
		tags = AlphaGo
                """
                


if not os.path.exists(os.path.expanduser("~/.config/foxGo.conf")):
    f = open(os.path.expanduser("~/.config/foxGo.conf"), "w")
    f.write(configContent)
    f.close()
    

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = mainWindow()
	w.show()
	sys.exit(app.exec_())
