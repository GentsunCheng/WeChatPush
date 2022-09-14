# coding=utf-8

import os
import sys
import signal
from datetime import datetime


def prt(mes):
    print(str(datetime.now().strftime('[%Y.%m.%d %H:%M:%S] ')) + str(mes))


if int(sys.version_info.major) < 3:
    prt('程序仅支持Python3.4及以上版本运行，程序强制停止运行')
    os._exit(0)

import requests
import importlib
import traceback
import platform
import time
from requests.packages import urllib3
from multiprocessing import Process, Manager

local_dir = str((os.path.split(os.path.realpath(__file__))[0]).replace('\\', '/'))
errorlog_clean = open(local_dir + '/error.log', 'w').close()
ppid = os.getppid()
pid = os.getpid()


def error_log(local):
    with open(local + '/error.log', 'a', encoding='utf-8') as f:
        f.write(str(datetime.now().strftime('[%Y.%m.%d %H:%M:%S] ')) + str(traceback.format_exc()) + '\n')
    prt('程序运行出现错误,错误信息已保存至程序目录下的error.log文件中')


try:
    import config
except:
    prt("读取配置文件异常,程序终止运行,请检查配置文件是否存在或语法是否有问题")
    error_log(local_dir)
    os._exit(0)

if int(config.async_components):
    import asyncio
    run_as_async = 1
else:
    run_as_async = 0

import itchat.content


def error(pid, ppid, errorlog_dir):
    error_log(errorlog_dir)
    prt('程序终止运行')
    system = str(platform.system())
    if system == 'Linux':
        os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
    elif system == 'Windows':
        os.system('taskkill /F /T /PID ' + str(pid))
    else:
        os.kill(int(ppid), signal.SIGTERM)


def config_update(value):
    try:
        while 1:
            try:
                importlib.reload(config)
            except:
                prt('配置获取异常,请检查配置文件是否存在/权限是否正确/语法是否有误')
                error(value.get('pid'), value.get('ppid'), value.get('local_dir'))
                break
            shield_mode_update = '0'
            newcfg = {'chat_push': str(config.chat_push), 'VoIP_push': str(config.VoIP_push), 'tdtt_alias': str(config.tdtt_alias),
                        'FarPush_regID': str(config.FarPush_regID), 'WirePusher_ID': str(config.WirePusher_ID),
                        'FarPush_Phone_Type': str(config.FarPush_Phone_Type), 'shield_mode': str(config.shield_mode),
                        'blacklist': list(config.blacklist), 'whitelist': list(config.whitelist), 'tdtt_interface': str(config.tdtt_interface), 
                        'FarPush_interface': str(config.FarPush_interface), 'WirePusher_interface': str(config.WirePusher_interface)}
            for a in list(newcfg.keys()):
                if str(a) == 'shield_mode':
                    if newcfg.get('shield_mode') != value.get('shield_mode'):
                        if int(newcfg.get('shield_mode')):
                            prt('切换为白名单模式：群聊' + str(newcfg.get('whitelist')) + '以及非群聊的消息将会推送')
                        else:
                            prt('切换为黑名单模式：' + str(newcfg.get('blacklist')) + '的消息将不会推送')
                        shield_mode_update = '1'
                elif str(a) == 'whitelist':
                    if not int(shield_mode_update) and newcfg.get(a) != value.get(a) and int(newcfg.get('shield_mode')):
                        prt('白名单更改：群聊' + str(newcfg.get(a)) + '以及非群聊的消息将会推送')
                elif str(a) == 'blacklist':
                    if not int(shield_mode_update) and newcfg.get(a) != value.get(a) and not int(newcfg.get('shield_mode')):
                        prt('黑名单更改：' + str(newcfg.get(a)) + '的消息将不会推送')
                elif str(value.get(a)) != str(newcfg.get(a)):
                    prt(str(a) + '更改,新' + str(a) + '值为' + str(newcfg.get(a)))
            value.update(newcfg)
            time.sleep(1)
    except KeyboardInterrupt:
        prt('由于触发了KeyboardInterrupt(同时按下了Ctrl+C等情况)，程序强制停止运行')
    except:
        error(value.get('pid'), value.get('ppid'), value.get('local_dir'))


def run(func):
    if int(run_as_async):
        asyncio.get_event_loop().run_until_complete(asyncio.gather(func))
    else:
        eval(str(func))


def data_send(url, **kwargs):
    for i in range(1, 5):
        try:
            response = requests.post(url, data=kwargs, timeout=5, verify=False)
            if response.status_code > 299:
                raise RuntimeError
        except:
            if str(i) == '4':
                prt('连续三次向接口发送数据超时/失败，可能是网络问题或接口失效，终止发送')
                break
            prt('向接口发送数据超时/失败，第' + str(i) + '次重试')
        else:
            prt('成功向接口发送数据↑')
            break


@itchat.msg_register(itchat.content.INCOME_MSG, isFriendChat=True, isGroupChat=True)
def simple_reply(msg):
    notify = 0
    if int(value.get('shield_mode')):
        if not int(msg.get('ChatRoom')) or str(msg.get('NickName')) in list(value.get('whitelist')): # 白名单模式，白名单群消息放行
            notify = 1
    elif str(msg.get('NickName')) not in list(value.get('blacklist')):
        notify =  1
    if int(notify) and not int(msg.get('NotifyCloseContact')):
        typesymbol = {
            itchat.content.TEXT: str(msg.get('Text')),
            itchat.content.FRIENDS: '好友请求',
            itchat.content.PICTURE: '[图片]',
            itchat.content.RECORDING: '[语音]',
            itchat.content.VIDEO: '[视频]',
            itchat.content.LOCATIONSHARE: '[共享实时位置]',
            itchat.content.CHATHISTORY: '[聊天记录]',
            itchat.content.TRANSFER: '[转账]',
            itchat.content.REDENVELOPE: '[红包]',
            itchat.content.EMOTICON: '[动画表情]',
            itchat.content.SPLITTHEBILL: '[群收款]',
            itchat.content.SHARING: '[卡片消息]',
            itchat.content.UNDEFINED: '[发送了一条消息]',
            itchat.content.VOIP: '[通话邀请]请及时打开微信查看',
            itchat.content.SYSTEMNOTIFICATION: '[系统通知]',
            itchat.content.ATTACHMENT: '[文件]' + str(msg.get('Text')),
            itchat.content.CARD: '[名片]' + str(msg.get('Text')),
            itchat.content.MUSICSHARE: '[音乐]' + str(msg.get('Text')),
            itchat.content.SERVICENOTIFICATION: str(msg.get('Text')),
            itchat.content.MAP: '[位置分享]' + str(msg.get('Text')),
            itchat.content.WEBSHARE: '[链接]' + str(msg.get('Text')),
            itchat.content.MINIPROGRAM: '[小程序]' + str(msg.get('Text')) }.get(msg['Type'])
        Name = str(msg.get('Name')) if str(msg.get('ChatRoom')) == '0' else '群聊 ' + str(msg.get('ChatRoomName'))
        if int(msg.get('ChatRoom')):
            typesymbol = str(msg.get('Name')) + ': ' + str(typesymbol)
        if str(msg.get('Type')) == str(itchat.content.SHARING):
            prt('[未知卡片消息，请在github上提交issue]: AppMsgType=' + str(msg.get('Text')))
        elif str(msg.get('Type')) == str(itchat.content.UNDEFINED):
            prt('[未知消息类型，请在github上提交issue]: MsgType=' + str(msg.get('Text')))
        else:
            prt(str(Name) + ': ' + str(typesymbol))
        if str(msg.get('Type')) == str(itchat.content.VOIP):
            if str(value.get('VoIP_push')) == '1' and str(value.get('tdtt_alias')) != '':
                data_send(str(value.get('tdtt_interface')), title='微信 ' + str(Name), content=str(typesymbol), alias=str(value.get('tdtt_alias')))
            elif str(value.get('VoIP_push')) == '2' and str(value.get('FarPush_regID')) != '':
                data_send(str(value.get('FarPush_interface')), title='微信 ' + str(Name), content=str(typesymbol), regID=str(value.get('FarPush_regID')), phone=str(value.get('FarPush_Phone_Type')), through='0')
            elif str(value.get('VoIP_push')) == '3' and str(value.get('WirePusher_ID')) != '':
                data_send(str(value.get('WirePusher_interface')), title='微信 ' + str(Name), message=str(typesymbol), id=str(value.get('WirePusher_ID')), type='WeChat_VoIP', action='weixin://')
            else:
                prt('配置有误，请更改配置')
        else:
            if str(value.get('chat_push')) == '1' and str(value.get('tdtt_alias')) != '':
                data_send(str(value.get('tdtt_interface')), title='微信 ' + str(Name), content=str(typesymbol), alias=str(value.get('tdtt_alias')))
            elif str(value.get('chat_push')) == '2' and str(value.get('FarPush_regID')) != '':
                data_send(str(value.get('FarPush_interface')), title='微信 ' + str(Name), content=str(typesymbol), regID=str(value.get('FarPush_regID')), phone=str(value.get('FarPush_Phone_Type')), through='0')
            elif str(value.get('chat_push')) == '3' and str(value.get('WirePusher_ID')) != '':
                data_send(str(value.get('WirePusher_interface')), title='微信 ' + str(Name), message=str(typesymbol), id=str(value.get('WirePusher_ID')), type='WeChat_chat', action='weixin://')
            else:
                prt('配置有误，请更改配置')


if __name__ == '__main__':
    try:
        urllib3.disable_warnings()
        run(itchat.check_login())
        run(itchat.auto_login(hotReload=True, enableCmdQR=2))
        value = Manager().dict()
        value.update({'pid': str(pid), 'ppid': str(ppid), 'local_dir': str(local_dir), 'chat_push': str(config.chat_push),
                        'VoIP_push': str(config.VoIP_push), 'tdtt_alias': str(config.tdtt_alias),
                        'FarPush_regID': str(config.FarPush_regID), 'WirePusher_ID': str(config.WirePusher_ID),
                        'FarPush_Phone_Type': str(config.FarPush_Phone_Type), 'shield_mode': str(config.shield_mode),
                        'blacklist': list(config.blacklist), 'whitelist': list(config.whitelist), 'tdtt_interface': str(config.tdtt_interface), 
                        'FarPush_interface': str(config.FarPush_interface), 'WirePusher_interface': str(config.WirePusher_interface)})
        conf_update = Process(target=config_update, args=(value, ))
        conf_update.daemon = True
        conf_update.start()
        if int(value.get('shield_mode')):
            prt('白名单模式：群聊' + str(value.get('whitelist')) + '以及非群聊的消息将会推送')
        else:
            prt('黑名单模式：' + str(value.get('blacklist')) + '的消息将不会推送')
        run(itchat.run())
    except KeyboardInterrupt:
        prt('由于触发了KeyboardInterrupt(同时按下了Ctrl+C等情况)，程序强制停止运行')
    except:
        error(pid, ppid, local_dir)
