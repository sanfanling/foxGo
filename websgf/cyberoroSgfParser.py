#! /usr/bin/python

from urllib import request as urllib2
from bs4 import BeautifulSoup
import re

class cyberoroSgfParser:

    def __init__(self):
        self.currentPage = 1
        self.pageLimited = None
    
    def getCatalogUrl(self):
        url = "http://www.cyberoro.com/bcast/gibo.oro?param=2&div=&Tdiv=B&Sdiv=&pageNo={0}&blockNo=1".format(self.currentPage)
        return url

    def getCatalog(self, url):
        req = urllib2.urlopen(url)
        page = req.read()
        req.close()
        return page.decode("euc-kr")

    def parseCatalog(self, e):
        pageList = []
        soup = BeautifulSoup(e, "html.parser")
        if self.pageLimited == None:
            r = re.findall("pageNo=.*?blockNo", e)
            self.pageLimited = int(r[-1].replace("pageNo=", "").replace("&blockNo", ""))
            
        k = soup.find_all("font", attrs = {"class":"gray11"})
        t = []
        for i in k:
            t.append(i.parent.parent)
        for j in t:
            tdList = j.find_all("td")
            date = tdList[0].font.string
            game = tdList[1].a.string
            url =re.search("http.*?sgf", tdList[1].a["href"]).group()
            bplayer = tdList[2].string
            wplayer = tdList[3].string
            tmpres = tdList[4].a.string
            res = "{0}(B) vs {1}(W) {2}".format(bplayer, wplayer, tmpres)
            pageList.append((url, game, res, date))
        return pageList

    def getSgf(self, q):
        req = urllib2.urlopen(q)
        sgf = req.read().decode("euc-kr")
        req.close()
        if sgf[:2] != "(;":
            sgf = sgf.replace("(", "(;", 1)
        return sgf

if __name__ == "__main__":
    p = cyberoroSgfParser()
    t = p.getCatalog(p.getCatalogUrl())
    l = p.parseCatalog(t)
    #print(l)
    print(p.getSgf(l[0][0]))
