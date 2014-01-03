#! /usr/bin/env python
# coding=utf-8
__author__ = 'jszhou'
from bottle import *
import hashlib
import xml.etree.ElementTree as ET
import urllib2
# import requests
import json
 
 
@get("/")
def checkSignature():
    token = 'this_is_my_token'
    signature = request.GET.get('signature', None)  # 拼写不对害死人那，把signature写成singnature，直接导致怎么也认证不成功
    timestamp = request.GET.get('timestamp', None)
    nonce = request.GET.get('nonce', None)
    echostr = request.GET.get('echostr', None)
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    # return "echostr: %s" % echostr
    if hashstr == signature:
        return echostr
    else:
        return None
 
 
def parse_msg():
    recvmsg = request.body.read()
    root = ET.fromstring(recvmsg)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg
 
 
 
@post("/")
def response_msg():
    # 拿到Post过来的数据
    # 分析数据（拿到FromUserName、ToUserName、CreateTime、MsgType和content）
    # 构造回复信息（将其中content变为返回给用户的信息）
    msg = parse_msg()
    textTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[%s]]></MsgType>
             <Content><![CDATA[%s]]></Content>
             <FuncFlag>0</FuncFlag>
             </xml>"""
    Content = 'this is my server info'
 
    # if Content is not False:
    echostr = textTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), msg['MsgType'], Content)
    return echostr
    # else:
    #     echostr = textTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), msg['MsgType'], "Content")
    #     return echostr
 
if __name__ == "__main__":
    # Interactive mode
    debug(True)
    run(host='127.0.0.1', port=8282, reloader=True)
else:
    # Mod WSGI launch
    import sae
    debug(True)
    os.chdir(os.path.dirname(__file__))
    app = default_app()
    application = sae.create_wsgi_app(app)