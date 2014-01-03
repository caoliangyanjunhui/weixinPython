# -*- coding: utf-8 -*-
'''
Created on 2013年10月28日

@author: 坏坏的忧伤
'''
import urllib.request
import json


class MenuManager:
    accessUrl = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=appid&secret=secret"
    delMenuUrl = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token="
    createUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token="
    getMenuUri="https://api.weixin.qq.com/cgi-bin/menu/get?access_token="
    def getAccessToken(self):
        f = urllib.request.urlopen(self.accessUrl)
        accessT = f.read().decode("utf-8")
        jsonT = json.loads(accessT)
        return jsonT["access_token"]
    def delMenu(self, accessToken):
        html = urllib.request.urlopen(self.delMenuUrl + accessToken)
        result = json.loads(html.read().decode("utf-8"))
        return result["errcode"]
    def createMenu(self, accessToken):
        menu = '''{
                 "button":[
                     {    
          "type":"click",
          "name":"今日歌曲",
          "key":"V1001_TODAY_MUSIC"
      },
      {
           "type":"view",
           "name":"歌手简介",
           "url":"http://www.qq.com/"
      },
      {
           "name":"菜单",
           "sub_button":[
            {"type":"click","name":"hello word","key":"V1001_HELLO_WORLD"},{"type":"click","name":"赞一下我们","key":"V1001_GOOD"}]}]}'''
        html = urllib.request.urlopen(self.createUrl + accessToken, menu.encode("utf-8"))
        result = json.loads(html.read().decode("utf-8"))
        return result["errcode"]
    def getMenu(self):
        html = urllib.request.urlopen(self.getMenuUri + accessToken)
        print(html.read().decode("utf-8"))
    

if __name__ == "__main__":
    wx = MenuManager()
    accessToken = wx.getAccessToken()
    #print(wx.delMenu(accessToken))   #删除菜单
    #print(wx.createMenu(accessToken))  #创建菜单
    wx.getMenu()
        