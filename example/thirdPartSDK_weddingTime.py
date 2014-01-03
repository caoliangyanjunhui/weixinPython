#coding:utf-8

import json, hashlib, time
import xml.etree.ElementTree as ET
from django.core.cache import cache
from lovewith.share.models import WeixinMp

class Weixin():
    def __init__(self):
        self.token = 'token' #请修改为自己的token
        self.shortcut = []
        self.shortcutData = {}

        cache_key = 'mt_weixin'
        #缓存时间(秒)
        cache_time = 5 * 60
        result = cache.get(cache_key)
        if result:
            self.shortcut = result.get('shortcut')
            self.shortcutData = result.get('shortcutData')
        else:
            reply_filter_data = WeixinMp.objects.all().order_by('-id')
            if reply_filter_data.exists():
                try:
                    auto_reply_data = json.loads(reply_filter_data[0].content)
                    for data in auto_reply_data:
                        self.shortcut.append('%s:%s' % (data.get('key'), data.get('name')))
                        self.shortcutData[data.get('key')] = data.get('news')


                    cache.set(cache_key, {
                        'shortcut': self.shortcut,
                        'shortcutData': self.shortcutData
                    }, cache_time)
                except:
                    pass



    #判断dict是否为空
    def is_not_none(self, params):
        for k, v in params.items():
            if v is None:
                return False
        return True



    # XMl To JSON
    def toJson(self, xml_body):
        #http://docs.python.org/2/library/xml.etree.elementtree.html#xml.etree.ElementTree.XML
        json_data = {}
        root = ET.fromstring(xml_body)
        for child in root:
            if child.tag == 'CreateTime':
                value = long(child.text)
            else:
                value = child.text
            json_data[child.tag] = value

        return json_data



    #cdata
    def addCdata(self, data):
        #http://stackoverflow.com/questions/174890/how-to-output-cdata-using-elementtree
        if type(data) is str or type(data) is unicode:
            return '<![CDATA[%s]]>' % data.replace(']]>', ']]]]><![CDATA[>')
        return data



    #JSON To XMl
    def toXml(self, xml_data, wrap_tag=None):
        xml = ''
        if wrap_tag:
            xml = '<%s>' % wrap_tag

        for item in xml_data:
            tag = item.keys()[0]
            value = item.values()[0]
            xml += '<%s>%s</%s>' % (tag, self.addCdata(value), tag)

        if wrap_tag:
            xml += '</%s>' % wrap_tag

        return xml



    #验证信息是否来自微信
    def validate(self, signature, timestamp, nonce, echostr):
        params = {
            'token': self.token,
            'timestamp': timestamp,
            'nonce': nonce
        }

        if self.is_not_none(params):
            sort_params = sorted([v for k, v in params.items()])
            client_signature = hashlib.sha1(''.join(sort_params)).hexdigest()

            if client_signature == signature:
                return echostr

        return False



    #回复文字信息
    def replyTextMsg(self, to_user, reply_msg):
        if to_user and reply_msg:
            response_msg = self.toXml([
                {'ToUserName': to_user},
                {'FromUserName': self.my_username},
                {'CreateTime': int(time.time())},
                {'MsgType': 'text'},
                {'Content': reply_msg}
            ], 'xml')

            return response_msg



    #处理新闻
    def getArticle(self, to_user, article_data):
        article_count = len(article_data)
        atricle_xml = '<xml>'

        base_xml_data = self.toXml([
                {'ToUserName': to_user},
                {'FromUserName': self.my_username},
                {'CreateTime': int(time.time())},
                {'MsgType': 'news'},
                {'ArticleCount': article_count}
            ])

        atricle_xml += base_xml_data
        atricle_xml += '<Articles>'

        for atricle in article_data:
            item_xml = self.toXml([
                {'Title': atricle.get('title')},
                {'Description': atricle.get('description')},
                {'PicUrl': atricle.get('picurl')},
                {'Url': atricle.get('url')}
            ], 'item')

            atricle_xml += item_xml

        atricle_xml += '</Articles>'
        atricle_xml += '</xml>'

        return atricle_xml


    #处理接收到的微信信息
    def getMessage(self, xml_body):
        json_data = self.toJson(xml_body)
        user = json_data.get('FromUserName')
        msg = json_data.get('Content')
        type = json_data.get('MsgType')
        event = json_data.get('Event' or None)

        self.my_username = json_data.get('ToUserName')

        if type == 'event' and event == 'subscribe':
            #添加订阅
            #self.addSubscribe(json_data)

            #回复订阅成功
            reply_msg = '/::$亲，终于等到您来了！感谢您关注【婚礼时光】官方订阅号，我们会每日分享给大家图文并茂的婚礼资讯或婚礼灵感，让热爱婚礼和正在筹备婚礼的亲们，及时获取最新婚礼信息和各类婚礼创意。婚礼时光创意社区官网：http://www.lovewith.me/，欢迎常来逛逛哦~直接回复“1”查看最新婚礼相关内容，回复“2”进入新娘SHOP选购最美婚纱婚品等，回复“3”查看婚礼类目和热门标签进行精准搜索。看到您喜欢的内容，记得转发到朋友圈和收藏哦~/:,@-D'
            
            return self.replyTextMsg(user, reply_msg)

        if type == 'text':
            article_data = self.shortcutData.get(msg)

            if article_data:
                return self.getArticle(user, article_data)
            else:
                if msg == 'lovewithme':
                    reply_text = '/::$ 么么哒'
                else:
                    reply_text = '进入复读机模式：您刚才说的是：%s。退出复读机模式，请输入暗号：lovewithme' % msg

                return self.replyTextMsg(user, reply_text)