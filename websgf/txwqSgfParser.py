#!/usr/bin/python

from urllib import request as urllib2
from bs4 import BeautifulSoup
import os.path


class txwqSgfParser:

    def __init__(self):
        self.currentPage = 1
        self.pageLimited = None
    
    def getCatalogUrl(self):
        url = "http://weiqi.qq.com/qipu/index/p/%d.html" %(self.currentPage,)
        return url

    def getCatalog(self, url):
        req = urllib2.urlopen(url)
        page = req.read()
        req.close()
        return page.decode("utf8")

    def parseCatalog(self, e):
        pageList = []
        soup = BeautifulSoup(e, "html.parser")
        if self.pageLimited == None:
            ul = soup.find(attrs = {"class":"pagination"})
            l = ul.find_all("a")[-1]["href"]
            u = os.path.basename(l)
            self.pageLimited = int(os.path.splitext(u)[0])
        table = soup.table
        for i in table.find_all("tr"):
            url = "http://weiqi.qq.com" + i.a["href"]
            game, res = i.a.h4.string.split("\xa0")
            time = i.find_all("td")[1].string
            pageList.append((url, game, res, time))
        return pageList

    def getSgf(self, q):
        req = urllib2.urlopen(q)
        f = req.read().decode("utf8")
        req.close()
        soup = BeautifulSoup(f, "html.parser")
        sgf = soup.find(attrs = {"id" : "player-container"}).string.strip()
        return sgf
        

if __name__ == "__main__":
    p = txwqSgfParser()
    t = p.getCatalog(p.getCatalogUrl())
    l = p.parseCatalog(t)
    print(p.getSgf(l[0][0]))
