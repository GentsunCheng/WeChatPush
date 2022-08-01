import requests
from requests.packages import urllib3
import itchat.content
import re

# 你的消息接收别名
# 例如aliasname = 'line'
aliasname = '推送别名'
# 你的消息推送黑名单,可为群名或者好友名，理论上可以按照格式无限添加
# 例如blacklist = ["相亲相爱一家人","法外狂徒张三","..."]
blacklist = ["black1", "balck2", "balck3"]


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
@itchat.msg_register(itchat.content.TEXT, isFriendChat=True)
def text_reply(msg):
    if msg.user.nickName not in blacklist:
        urllib3.disable_warnings()
        print(msg.user.nickName + msg.text)
        requests.get('https://send.tdtt.top/', params={'title': '%s' % msg.user.nickName, 'content': '%s' % msg.text, 'alias': '%s' % aliasname}, verify=False)

@itchat.msg_register([itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.ATTACHMENT, itchat.content.VIDEO], isGroupChat=True)
@itchat.msg_register([itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.ATTACHMENT, itchat.content.VIDEO], isFriendChat=True)
def download_files(msg):
    if msg.user.nickName not in blacklist:
        urllib3.disable_warnings()
        typesymbol = {
            itchat.content.PICTURE: '[图片]',
            itchat.content.RECORDING: '[音频]',
            itchat.content.ATTACHMENT: '[文件]',
            itchat.content.VIDEO: '[视频]', }.get(msg.type, 'fil')
        print(msg.user.nickName + typesymbol)
        requests.get('https://send.tdtt.top/', params={'title': '%s' % msg.user.nickName, 'content': '%s' % typesymbol, 'alias': '%s' % aliasname}, verify=False)

@itchat.msg_register([itchat.content.MAP, itchat.content.SHARING, itchat.content.CARD], isGroupChat=True)
@itchat.msg_register([itchat.content.MAP, itchat.content.SHARING, itchat.content.CARD], isFriendChat=True)
def receive_msg(msg):
    if msg.user.nickName not in blacklist:
        if msg['Type'] == 'Card':
            urllib3.disable_warnings()
            print(msg['RecommendInfo']['NickName'])
            requests.get('https://send.tdtt.top/', params={'title': '%s' % msg.user.nickName, 'content': '向你推荐了：%s' % msg['RecommendInfo']['NickName'], 'alias': '%s' % aliasname}, verify=False)
        elif msg['Type'] == 'Map':
            urllib3.disable_warnings()
            x, y, location = re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
            locationname = '地址：' + location + '\n经纬度：' + x + ',' + y
            print(locationname)
            requests.get('https://send.tdtt.top/', params={'title': '%s' % msg.user.nickName, 'content': '%s' % locationname, 'alias': '%s' % aliasname}, verify=False)
        elif msg['Type'] == 'Sharing':
            urllib3.disable_warnings()
            Sharing = '分享：' + msg['Text'] + '\n链接：' + msg['Url']
            print(Sharing)
            requests.get('https://send.tdtt.top/', params={'title': '%s' % msg.user.nickName, 'content': '%s' % Sharing, 'alias': '%s' % aliasname}, verify=False)

if __name__ == '__main__':
    itchat.check_login()
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    itchat.run()
