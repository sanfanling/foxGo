#! /usr/bin/python

from urllib import request as urllib2
from bs4 import BeautifulSoup
import re


class sinawqSgfParser:

    def __init__(self):
        self.currentPage = 0
        self.pageLimited = 976

    def getCatalogUrl(self):
        url = "http://duiyi.sina.com.cn/gibo/new_gibo.asp?cur_page=%d" %(self.currentPage,)
        return url
    
    def getCatalog(self, url):
        req = urllib2.urlopen(url)
        page = req.read()
        req.close()
        return page.decode("gbk")

    def parseCatalog(self, e):
        pageList = []
        soup = BeautifulSoup(e, "html.parser")
        k = soup.find_all(attrs = {"align":"center", "bgcolor":"#FFFFFF", "class":"body_text1"})
        for i in k:
            td = i.find_all("td")
            time = td[0].string
            try:
                url = re.search("http.*?sgf", td[1].a["href"]).group()
            except:
                continue
            bplayer = "%s（黑）" %(td[1].string,)
            wplayer = "%s（白）" %(td[2].string,)
            game = "%s - %svs%s" %(td[3].string, bplayer, wplayer)
            res = td[4].string
            #res = "%s vs %s，%s" %(bplayer, wplayer, r)
            pageList.append((url, game, res, time))
        return pageList

    def getSgf(self, q):
        req = urllib2.urlopen(q)
        sgf = req.read().decode("gbk")
        req.close()
        if sgf[:2] != "(;":
            sgf = sgf.replace("(", "(;", 1)
        return sgf
            
             
if __name__ == "__main__":
    p = sinawqSgfParser()
    t = p.getCatalog()
    l = p.parseCatalog(t)
    print(p.getSgf(l[0][0]))
