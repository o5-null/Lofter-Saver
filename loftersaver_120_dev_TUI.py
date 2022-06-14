import requests
from readability import Document
from bs4 import BeautifulSoup

from pathlib import Path
import os
import time
import sys
from urllib.parse import quote

from tqdm import tqdm

import core

# 初始化
local_time = time.strftime("%y/%m/%d", time.localtime())
if not Path('set.json').exists():
    local_dir = str(Path(str(Path.cwd().resolve())+'/Download'))
    set = {}
    set['download'] = local_dir
    core.save_set(set)
if Path('set.json').exists():
    set = core.get_set()


def start_download(answer):
    if '/post/' in answer:  # 单文章下载
        info = core.gets(answer)
        info = core.lofter_info(info)
        if info['title'] == 'null':
            print('链接错误，请重试')#发送消息
            return 'error'
        else:
            print(info['title']+' 下载中')#发送消息
            core.lofter_down(info,set['download'])
            print(info['title']+' 下载完成')#发送消息
            return 'fine'
    elif 'lofter.com' in answer:
        list = core.lofter_post_list(answer)
        if list == 'null':
            print('链接错误，请重试')#发送消息
            return 'error'
        else:
            answer = input('批量下载任务解析完成，共有'+str(len(list))+'个任务(回车开始下载，输入任意内容退出下载:')
            if not str(answer) == '':
                print('下载已退出')
                return 'fine'
            print('批量下载任务已开始，共有'+str(len(list))+'个任务')#发送消息
            for url in tqdm(list,desc='批量下载进行中：',unit='doc'):
                info = core.gets(url)
                if info == 'null':
                    print('链接错误，自动跳过')#发送消息
                    continue
                info = core.lofter_info(info)
                if info == 'null':
                    print('链接错误，自动跳过')#发送消息
                    continue
                core.lofter_down(info, set['download'])
                print(info['title']+' 下载完成')#发送消息
            print('批量任务已完成，共下载'+str(len(list))+'个文章')#发送消息
    print('链接错误，请重试')
    return 'error'




# tui创建
#主函数
print('LofterSaver 1.2 Dev')
print('Power by python')
print('Made in Mr.G')
print('程序初始化。。。。')

while 1==1:
        answer = input('请粘贴需解析地址(输入set调整设置,输入exit退出)：')
        if answer == 'set':
            while 1==1:
                set = core.get_set()
                print('1.当前下载目录：'+set['download'])
                answer = input('输入1修改设置(输入0退出设置)：')
                if answer == '0':
                    break
                if answer == '1':
                    answer = input('输入新指定的下载目录（若留空指定为'+str(Path(str(Path.cwd().resolve())+'/Download)：')))
                    if answer == '':
                        set['download'] = str(Path(str(Path.cwd().resolve())+'/Download'))
                        core.save_set(set)
                        print('已修改下载目录')
                        continue
                    if answer != '':
                        os.makedirs(answer,exist_ok=True)
                        if os.path.exists(answer):
                            print('下载目录可用')
                            set['download'] = answer
                            core.save_set(set)
                            print('已修改下载目录')
                            continue
                print('输入不正确')
            continue
        if answer == 'exit':
            sys.exit()
        code = start_download(answer)
exit()
