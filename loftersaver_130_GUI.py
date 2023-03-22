from pathlib import Path
import os
from datetime import datetime
import time
import sys
import re
import requests

import threading #多进程库
from tqdm import tqdm
import pywebio as io
out = io.output
ioin = io.input
pin = io.pin

import core#导入核心

# 初始化
local_time = time.strftime("%y/%m/%d", time.localtime())
if not Path('set.json').exists():
    local_dir = str(Path(str(Path.cwd().resolve())+'/Download'))
    set = {}
    set['download'] = local_dir
    core.save_set(set)
if Path('set.json').exists():
    set = core.get_set()

#开始下载任务
def start_download():
    list = core.downlist()#获取下载列表
    while len(list) != 0:#当下载任务不为0时
        lofter_info_down(list[0],set['download'])#下载任务
        time.sleep(0.3)
        core.del_downlist(list[0])#删除下载完成的任务

        #添加到下载完成列表
        fin = core.finlist()
        fin.append(list[0])
        core.finlist(fin)

        #刷新下载进度条
        value = len(fin) / len(list)
        out.set_processbar('down_process',value)
        list = core.downlist()#刷新下载任务
    out.toast('下载任务已清空', position='center', color='success', duration=0)#显示完成通知
    show_down_list()
    show_fin_list()
    return

#显示下载列表
def show_down_list():
    """
    处理下载列表并显示
    """
    #加载任务列表
    data_list = core.downlist()#获取需要下载的列表
    if len(data_list) == 0:#如果列表为空则等待
        time.sleep(1)
        show_down_list()
    show_list = []
    #初始化
    for list_one in data_list:#遍历创建下载列表
        a = out.put_row([
                out.put_text(list_one['title']),#TODO 创建标题
                #out.put_button('暂停',onclick=lambda:core.patch_pause_task(list_one['control_name']),color='warning'),#暂停按钮
                ]).style('border: 1px solid #e9ecef;border-radius: .25rem')
        # 创建显示
        show_list.append(a)
    #显示列表
    with out.use_scope('down_work',clear=True):#清除域
        out.put_column(show_list)

    #刷新状态
    while 1==1:
        time.sleep(1)#等待1秒
        #如果下载列表更新
        if data_list != core.downlist():#如果现在维护的和存储的不一样
            show_down_list()

#显示下载列表
def show_fin_list():
    """
    处理下载列表并显示
    """
    #加载任务列表
    data_list = core.finlist()#获取需要下载的列表
    if len(data_list) == 0:#如果列表为空则等待
        time.sleep(1)
        show_fin_list()
    show_list = []
    #初始化
    for list_one in data_list:#遍历创建下载列表
        a = out.put_row([
                out.put_text(list_one['title']),#TODO 创建标题
                #out.put_button('暂停',onclick=lambda:core.patch_pause_task(list_one['control_name']),color='warning'),#暂停按钮
                ]).style('border: 1px solid #e9ecef;border-radius: .25rem')
        # 创建显示
        show_list.append(a)
    #显示列表
    with out.use_scope('down_fin',clear=True):#清除域
        out.put_column(show_list)

    #刷新状态
    while 1==1:
        time.sleep(1)#等待1秒
        #如果下载列表更新
        if data_list != core.finlist():#如果现在维护的和存储的不一样
            show_fin_list()

#下载内容
def lofter_info_down(info,local_dir):
    text = info['info'] #清洗文本
    #获取txt格式
    txt = text.replace('</p>','\n')#doc.summary()为提取的网页正文但包含html控制符，这一步是替换换行符
    txt = re.sub(r'</?\w+[^>]*>', '', txt)      #这一步是去掉<****>内的内容
    #获取html格式
    html = text.replace('\n','')#去除换行符
    print('数据分析完毕')
    #去除错误编码
    info['title'] = core.clean_name(info['title'])
    #创建根文件夹
    save_dir =str(Path(str(local_dir)+'/'+core.clean_name(info['title'])).resolve())
    os.makedirs(save_dir,exist_ok=True)

    #保存元数据为json以便调用
    print('保存元数据')
    core.save_json(Path(save_dir+'/entry.json'),info)

    #创建下载
    if len(info['img']) != 0:
        print('启动媒体数据本地化')
        os.makedirs(Path(save_dir+'/img'),exist_ok=True)#创建图片文件夹
        core.down_img(info['img'],Path(save_dir+'/img'))
        down_name = os.listdir(Path(save_dir+'/img'))
        for change_name in down_name:
            if 'img%2F' in change_name:
                #捕获错误段
                true_name = change_name.split('%2F')[-1]
                #true_name = true_name[3:]
                os.rename(Path(save_dir+'/img/'+change_name),Path(save_dir+'/img/'+true_name))
        print('媒体文件下载完毕')

    #html本地化
    # 截取图片文件名
    img_list = []
    for url in info['img']:
        img_name = url.split('/').pop()
        img_list.append(img_name)
    img_html = ''
    for local_img in img_list:#创建图片html代码
        img_html += '<img src="img/'+local_img+'" alt="some_text">'
    #创建index.html
    if html != 'null':
        html = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>'+info['title']+'</title>'+img_html+html#添加标题和头标识
        core.save_txt(Path(save_dir+'/index.html'),html)
    if txt != 'null':#保存纯文本
        core.save_txt(Path(save_dir+'/index.txt'),txt)
    print('索引链接创建完成')
    print('本地化完成')

    core.del_downlist(info)#删除下载任务
    return

#提取页面文章列表
def lofter_post_list(url):
    page = 0
    post = []
    while 1==1:
        page += 1
        if page == 1:
            post_url = url
        else:
            post_url = url+'?page='+str(page)
        data = core.gets(post_url)
        if data == 'null':
            return 'null'
        kk = re.compile('"(https://.*?\.lofter\.com/post/.*?_.*?)"')
        post_list = kk.findall(data)
        print('正在解析第'+str(page)+'页')
        out.toast('正在解析第'+str(page)+'页',position='left', color='info', duration=1)#弹出提示
        post_list = core.dic(post_list)
        if len(core.dic(post + post_list)) - len(post) == 0:
            break
        post = core.dic(post + post_list)
        print('本页提取'+str(len(post_list))+'个文章')
        print('已提取'+str(len(post))+'个文章')
        out.toast('已提取'+str(len(post))+'个文章',position='left', color='info', duration=1)#弹出提示
    print('共提取'+str(len(post))+'个文章')
    out.toast('已提取'+str(len(post))+'个文章',position='left', color='success', duration=0)#弹出提示
    return post

#显示文档信息
def lofter_print(info):
    #清除旧显示内容
    out.clear('info')
    with out.use_scope('info'):#进入视频信息域
        with out.use_scope('up_info'):#切换到up信息域
            face = requests.get(info['writer']['img']).content#缓存图片
            out.put_row([
                    None,
                    out.put_image(face,height='50px').style('margin-top: 1rem;margin-bottom: 1rem;border:1px solid;border-radius:50%;box-shadow: 5px 5px 5px #A9A9A9'),
                    None,
                    out.put_column([
                        None,
                        out.put_text(info['writer']['name']).style('font-size:1.25em;line-height: 0'),
                        ],size='1fr 1fr'),
                    None
                ],size='1fr 50px 25px auto 1fr').style('border: 1px solid #e9ecef;border-radius: .25rem')#限制up头像大小
        info_title = out.put_text(info['title']).style('border: 1px solid #e9ecef;border-radius: .25rem;font-size:1.5em;font-weight:bold;text-align:center')#标题
        out.put_column([info_title],size='auto 10px auto 10px auto').style('margin-top: 0.5rem;margin-bottom: 0.5rem')#设置为垂直排布
        control_buttom = ioin.actions(buttons=[{'label':'添加下载','value':'0'},{'label':'退出界面','value':'1','color':'danger'}])#创建按键
        if control_buttom == '0':#如果选择下载被勾选部分
            downlist = core.downlist()#获取下载列表
            downlist.append(info)#添加任务至下载列表
            core.downlist(downlist)#写入下载列表
        elif control_buttom == '1':#如果选择退出
            return 'out'

#显示批量信息
def lofter_list_print(list:list):
    #清除旧显示内容
    out.clear('info')
    with out.use_scope('info'):#进入视频信息域
        #显示信息获取进度
        out.put_text('获取信息中。。。').style('border: 1px solid #e9ecef;border-radius: .25rem;font-size:1em;font-weight:bold;text-align:center')#TODO 创建标题
        out.put_processbar('get_api')#进度条
        a = 0
        info_list = []
        for url in list:
            a += 1
            print(url)
            answer = lofter_down(url)#申请数据
            out.set_processbar('get_api',a / len(list))#刷新进度条
            info_list.append(answer)
        #遍历创建标题列表
        show_list = []
        for list_one in info_list:#遍历创建下载列表
            a = out.put_row([
                        out.put_text(list_one['title']).style('border: 1px solid #e9ecef;border-radius: .25rem;font-size:1em;font-weight:bold;text-align:center')#标题
                    ]).style('border: 1px solid #e9ecef;border-radius: .25rem')
            # 创建显示
            show_list.append(a)
        out.put_column(show_list).style('margin-top: 0.5rem;margin-bottom: 0.5rem')#设置为垂直排布
        control_buttom = ioin.actions(buttons=[{'label':'添加下载','value':'0'},{'label':'退出界面','value':'2','color':'danger'}])#创建按键
        if control_buttom == '0':#如果选择下载被勾选部分
            downlist = core.downlist()#获取下载列表
            downlist = downlist + info_list#添加任务至下载列表
            core.downlist(downlist)#写入下载列表
            return
        elif control_buttom == '1':#如果选择退出
            return 'out'

#lofter处理下载
def lofter_down(url):
    #格式化链接
    print(url)
    id = re.findall('/post/(.*?_.*)',url)[0]
    id = id.split('_')
    targetblogid = int(id[0],16)
    blogid = int(id[1],16)
    #发送请求
    print('tar '+str(targetblogid))
    print('bl '+str(blogid))
    answer = core.lofter_api(targetblogid,blogid)
    if answer['status'] != 200:#如果返回不正常
        #弹出错误弹窗
        out.toast(answer['msg'],color='error',duration='0')#弹出错误弹窗
        return
    return answer
    


#启动解析
def start_url():
    url = pin.pin['url_input']#获取输入
    if 'lofter' in url:#如果为lofter地址
        if '/post/' not in url:#尝试批量获取
            list = lofter_post_list(url)
            lofter_list_print(list)#显示列表
            #清除旧显示内容
            out.clear('info')
            return
        answer = lofter_down(url)
        #显示内容
        lofter_print(answer)
        #清除旧显示内容
        out.clear('info')
        return


#主函数
def main():#主函数
    print('主函数启动')
    #初始化
    out.scroll_to('main','top')
    out.clear('main')
    #创建横向标签栏
    scope_url = out.put_scope('url')#创建url域
    scope_set = out.put_scope('set')#创建set域
    scope_down = out.put_scope('down')#创建down域
    out.put_tabs([{'title':'链接解析','content':scope_url},{'title':'下载列表','content':scope_down},{'title':'设置','content':scope_set}])#创建
        

    #创建url输入框
    with out.use_scope('url'):#进入域
        pin.put_input('url_input',label='请输入链接',type='text')#限制类型为url,使用check_input_url检查内容
        out.put_button(label='解析链接',onclick=start_url).style('width: 100%')#创建按键
        out.put_scope('info')
        
    #创建下载列表
    with out.use_scope('down'):
        scope_down_work = out.put_scope('down_work')
        scope_down_fin = out.put_scope('down_fin')
        start_download_buttom = out.put_button('开始下载任务',onclick=start_download,color='success')#开始下载任务
        del_download_buttom = out.put_button('清空下载任务',onclick=lambda:core.downlist([]),color='danger')#开始下载任务
        out.put_row([None,start_download_buttom,None,del_download_buttom,None],size='1fr auto 1fr auto 1fr')#设置横向排布
        out.put_processbar('down_process')#设置下载进度条
        out.put_tabs([{'title':'下载中','content':scope_down_work},{'title':'下载完成','content':scope_down_fin}])#创建横向标签栏

    #创建设置
    with out.use_scope('set'):#进入域
        pass
    
    #启动副进程
    if not show_down_list_core.is_alive():
        print('启动下载任务管理')
        io.session.register_thread(show_down_list_core)
        show_down_list_core.daemon = True#设为守护进程
        show_down_list_core.start()
    if not show_fin_list_core.is_alive():
        print('启动完成任务管理')
        io.session.register_thread(show_fin_list_core)
        show_fin_list_core.daemon = True#设为守护进程
        show_fin_list_core.start()



# gui创建
#主函数
print('LofterSaver 1.3 Dev')
print('Power by python')
print('Made in Mr.G')
print('程序初始化。。。。')
show_down_list_core = threading.Thread(target=show_down_list)#下载列表
show_fin_list_core = threading.Thread(target=show_fin_list)#完成列表
io.config(title='Jithon 2.0 Beta',description='基于python的webui实现',theme='yeti')
print('主程序启动,如未自动跳转请打开http://127.0.0.1:8080')
io.start_server(main,host='127.0.0.1',port=8080,debug=True,cdn=False,auto_open_webbrowser=True)