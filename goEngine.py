#!/usr/bin/python


class go:
    
    def __init__(self):
        self.stepsGo = []
        self.stepsGoDict = {} #records any existed chesses on board, with chess color info, can append and remove step
        self.stepsGo_Test = []
        self.stepsGoEasy_blackTmp = []
        self.stepsGoEasy_whiteTmp = []
        self.stepNum = 0
        self.goColor = "black"
        self.x = 0
        self.y = 0
    
    def makeStepSafe(self):
        deadList = self.checkEnemyBlockBreath(self.x, self.y, dict(self.stepsGoDict), self.goColor)
        deadListLen = len(deadList)
        self.stepNum += 1
        if deadListLen == 0:
            #print("review模式：无死棋")
            #self.stepsGoEasy.append((self.x, self.y))
            self.stepsGoDict[(self.x, self.y)] = (self.goColor, self.stepNum)
            self.endStepSuccess()
            return (1, 0)
        else:
            #print("review模式：有死棋")
            #self.stepsGoEasy.append((self.x, self.y))
            self.stepsGoDict[(self.x, self.y)] = (self.goColor, self.stepNum)
            chess = self.eatChess(deadList)
            self.endStepSuccess()
            return (2, chess)
        
    
    def makeStep(self):
        if (self.x, self.y) not in self.stepsGoDict.keys():
            haveBreath = self.checkBlockBreath(dict(self.stepsGoDict), self.goColor, self.getBlock(self.x, self.y, dict(self.stepsGoDict), self.goColor, []), True, self.x, self.y)
            deadList = self.checkEnemyBlockBreath(self.x, self.y, dict(self.stepsGoDict), self.goColor)
            deadListLen = len(deadList)
            if haveBreath and deadListLen == 0:
                print("has liberty, legal move!")
                self.stepSuccess()
                self.endStepSuccess()
                self.changeColor()
                return (1, 0)
            elif haveBreath and deadListLen != 0:
                print("has liberty, legal move, take!")
                print(deadList)
                self.stepSuccess()
                chess = self.eatChess(deadList)
                self.endStepSuccess()
                self.changeColor()
                return (2, chess)
            elif not haveBreath and deadListLen == 0:
                print("no libery, no take, illegal move!")
                return (0, 0)
            elif not haveBreath and deadListLen != 0:
                print("no liberty，but legal move, take! it maybe a ko, check!")
                print(deadList)
                if not self.checkJie(deadList):
                    self.stepSuccess()
                    chess = self.eatChess(deadList)
                    self.endStepSuccess()
                    self.changeColor()
                    return (2, chess)
                else:
                    print("it's a ko, illegal move!")   
                    return (0, 0)
        return (0, 0)

    def stepSuccess(self):
        self.stepNum += 1
        self.stepsGo.append((self.stepNum, self.goColor, self.x, self.y))            
        #self.stepsGoEasy.append((self.x, self.y))
        self.stepsGoDict[(self.x, self.y)] = (self.goColor, self.stepNum)
    
    def endStepSuccess(self):
        if self.goColor == "black":
            self.stepsGoEasy_blackTmp = list(self.stepsGoDict.keys())
        else:
            self.stepsGoEasy_whiteTmp = list(self.stepsGoDict.keys())
    
    def changeColor(self):
        if self.goColor == "black":
            self.goColor = "white"
        else:
            self.goColor = "black"
    
    def eatChess(self, deadChessList):
        p = 0
        for j in deadChessList:
            del self.stepsGoDict[j]
            p += 1
        return p
            
    def checkJie(self, deadList):
        if len(deadList) != 1:
            return False
        else:
            stepsGoEasyTmp = list(self.stepsGoDict.keys())
            stepsGoEasyTmp.append((self.x, self.y))
            stepsGoEasyTmp.remove(deadList[0])
            
            if self.goColor == "black":
                stepsGoEasyTmp.sort()
                self.stepsGoEasy_blackTmp.sort()
                if stepsGoEasyTmp == self.stepsGoEasy_blackTmp:
                    return True
                else:
                    return False
            else:
                stepsGoEasyTmp.sort()
                self.stepsGoEasy_whiteTmp.sort()
                if stepsGoEasyTmp == self.stepsGoEasy_whiteTmp:
                    return True
                else:
                    return False
    
    def getBlock(self, x, y, tmpDict, goColor, blockList = []):
        #print("getBlock: 正在搜寻%d,%d周边本方子，并计入块列表" %(x,y))
        blockList.append((x, y))
        tmpDict[(x, y)] = ("blabla", 0)
        #print("getBlock: 将本身设置为中性色")
        for offsetx, offsety in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            try:
                logic = tmpDict[(x+offsetx, y+offsety)][0] == goColor
            except:
                logic = False
            if 0 < x+offsetx < 20 and 0 < y+offsety < 20 and logic:
                #print("getBlock: 有子联通")
                self.getBlock(x+offsetx, y+offsety, tmpDict, goColor, blockList)
        #print("getBlock: ")
        #print(blockList)
        return blockList
    
    def checkBlockBreath(self, tmpDict, goColor, blockList, checkMyBlock = True, a = 0, b = 0):
        if checkMyBlock:
            tmpDict[(a, b)] = ("blabla", 0)
        for (x, y) in blockList:
            for offsetx, offsety in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                #print("checkBlockBreath: 正在查找块中%s,%s的气" %(x, y))
                if 0 < x+offsetx < 20 and 0 < y+offsety < 20 and (x+offsetx, y+offsety) not in tmpDict.keys():
                    #print("checkBlockBreath: 整块本身有气")
                    return True
        #print("checkBlockBreath: 整块没有气！！")
        return False
    
    def checkEnemyBlockBreath(self, x, y, tmpDict, goColor):
        deadChess = []
        #print("checkEnemyBlockBreath: 无论本身有无气，假定可落子，并设为中性色，开始查找周边敌子的气")
        tmpDict[(x,y)] = ("blabla", 0)
        for offsetx, offsety in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x+offsetx, y+offsety) not in tmpDict.keys() or tmpDict[(x+offsetx, y+offsety)][0] == goColor:
                #print("checkEnemyBlockBreath: 此区块无子，或是本方子，或是边界，跳过")
                continue
            else:
                if goColor == "white":
                    t = "black"
                else:
                    t = "white"
                #print("checkEnemyBlockBreath: 查找敌子区块(%d,%d)" %(x+offsetx, y+offsety))
                expr = 'self.getBlock(x+offsetx, y+offsety, dict(self.stepsGoDict), "%s", [])' %(t,)
                blockList = eval(expr)
                #print("checkEnemyBlockBreath: 敌子区块")
                #print(blockList)
                if self.checkBlockBreath(dict(tmpDict), t, blockList): 
                    #print("checkEnemyBlockBreath: 此区块敌子有气！跳过")
                    continue
                else:
                    #print("checkEnemyBlockBreath: 此区块敌子有死棋！死棋块计入列表")
                    for j in blockList:
                        if j not in deadChess:
                            deadChess.append(j)
                        else:
                            break
        return deadChess
