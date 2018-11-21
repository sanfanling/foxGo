#!/bin/use/python

from sgf import sgf


class sgfData:
    
    def __init__(self, fUrl):
        f = open(fUrl, "r")
        collection = sgf.parse(f.read())
        f.close()
        self.game = collection.children[0]
        self.head = self.game.root.properties
        self.rest = self.game.rest
        
    
    def getTitle(self):
        try:
            return self.head["GN"][0]#txwq
        except:
            return self.head["TE"][0]#sinawq
        
    
    def getBlackPlayer(self):
        return self.head["PB"][0]
    
    def getWhitePlayer(self):
        return self.head["PW"][0]
    
    def getDate(self):
        try:
            return self.head["DT"][0]#foxwq
        except:
            return self.head["RD"][0]#xlwq
    
    def getResult(self):
        return self.head["RE"][0]
    
    def getKomi(self):
        try:
            return int(self.head["KM"][0])/100#foxwq
        except:
            return self.head["KO"][0]#xlwq
    
    def getBlackPlayerDan(self):
        return self.head["BR"][0]
    
    def getWhitePlayerDan(self):
        return self.head["WR"][0]
    
    def getStepsData(self, iterator):
        stepList = []
        j = 0
        for i in iterator:
            j += 1
            if "B" in i.properties:
                goColor = "black"
                xname = i.properties["B"][0][0]
                yname = i.properties["B"][0][1]
            else:
                goColor = "white"
                xname = i.properties["W"][0][0]
                yname = i.properties["W"][0][1]
            x = ord(xname)-96
            y = ord(yname)-96
            stepList.append((j, goColor, x, y))
        return stepList
    

    def getCommentsData(self, iterator, variationComment = False):
        commentDict = {}
        comment = ""
        j = 0
        for i in iterator:
            j += 1
            if "C" in i.properties:
                comment = i.properties["C"][0]
                commentDict[j] = comment
        if not variationComment:
            return commentDict
        else:
            return comment
    
    def getVariations(self):
        p = 0
        variationDict = {}
        for i in self.rest:
            p += 1
            if len(i.variations) != 0:
                variationList = []
                for j in i.variations[1:]:
                    v = self.recursionNode(j, [], 0)
                    subList = self.getStepsData(v)
                    subComment = self.getCommentsData(v, True)
                    subList.append(subComment)
                    variationList.append(subList)
                variationDict[p] = variationList
        return variationDict

    def recursionNode(self, node, var, k):
        k += 1
        var.append(node)
        #var.append([k, self.getColor, self.getx, self.gety])
        node = node.next
        if node == None:
            return var
        else:
            self.recursionNode(node, var, k)
        return var


if __name__ == "__main__":
    a = sgfData("11.sgf")
    print(a.getKomi())
    print(a.getBlackPlayer())
    print(a.getCommentsData())
    
