import requests
from readability import Document
from bs4 import BeautifulSoup
import remi.gui as gui
from remi.gui import *
from remi import start,App

import re
import os
import sys
import time
import json

local_dir = os.getcwd()+'/Download'


#清洗文件名
def clean_name(strs):
    strs = re.sub(r'/:<>?/\^|', "",strs)
    # 去除不可见字符
    return strs


#下载列表去重
def dic(info):
    new_list = []#创建临时列表
    for a in info:
        if a == 'null':
            continue
        if not a in new_list:
            new_list.append(a)
    return new_list

def get_set():
    if os.path.exists('downlist.json'):
        with open('downlist.json','r') as f:
            list = json.load(f)
        return list
    return []

def save_set(set):
    with open('downlist.json','w') as f:
        json.dump(set,f)

def get_setjson():
    with open('set.json','r') as f:
        set = json.load(f)
    return set

def save_setjson():
    with open('set.json','w') as f:
        json.dump(set,f)


#readability接口解析
def clean_1(data): #获取网站正文文本
    doc = Document(data)
    html = doc.summary()
    #获取页面标题
    title = doc.title()
    #对html进行修正以使img正常加载
    need = '<figure class="img-box" contenteditable="false">'
    html = html.replace(need,'<figure>')
    need = '<figure contenteditable="false" class="img-box">'
    html = html.replace(need,'<figure>')
    html = html.replace('data-src','src')
    html = html.replace('src="//','src="https://')
    #获取txt格式
    txt = doc.summary().replace('</p>','\n')#doc.summary()为提取的网页正文但包含html控制符，这一步是替换换行符
    txt = re.sub(r'</?\w+[^>]*>', '', txt)      #这一步是去掉<****>内的内容
    #创个字典存放数据
    fine = {}
    fine['title'] = title
    fine['html'] = html
    fine['txt'] = txt
    return fine

#url2io接口
def clean_2(url):
    token = 'MeTlIPmSRjmWgaNa9GzDAw' # 开发者 token, 注册后可得，注意保密
    fields = ','.join(['next','txt']) # 可选字段# HTTP Get
    result = brower.get(api_url+'article?token='+token+'&url='+url+'&fields='+fields,headers=headers).json()
    #创个字典存放数据
    fine = {}
    fine['title'] = result['title']
    fine['html'] = result['content']
    return fine

def save_json(name,data):
    with open(name,'w',encoding='utf-8') as f:
        json.dump(data,f)

def save_txt(name,data):
    with open(name,'w',encoding='utf-8') as f:
        f.write(data)

#下载图片
def down_img(img,save_dir):
    sep = '\n'
    if img == 'null':
        return
    with open(save_dir+'/img/url.txt','w') as f:
        f.write(sep.join(img))
    os.system('aria2c --quiet true -j 10 --dir="'+save_dir+'/img" -i "'+save_dir+'/img/url.txt"')
    return


def lofter_info(data):
    text = clean_1(data)
    sp = BeautifulSoup(data,'lxml')
    #标题提取
    title_data = sp.find_all(name="meta")
    title = '0'
    for data in title_data:
        if "Description" in str(data):
            title = data['content']
            break
    if len(title) >= len(text['title'])*2:#标题修正
        title = text['title']
    #图片提取
    image_data = sp.find_all(imggroup="gal")
    if len(image_data) != 0:
        image_url = re.findall('src="(https://.*?g)\?',str(image_data))
    #检查是否有有效文本信息
    test = text['txt'].replace('\n','')
    if test == '':
        test = 'null'
    #整理数据
    info = {}
    info['html'] = 'null'
    info['txt'] =  'null'
    if test != 'null':
        info['html'] = text['html']
        info['txt'] = text['txt']
    info['title'] = title
    if len(image_data) != 0:
        info['image'] = dic(image_url)
    if len(image_data) == 0:
        info['image'] = 'null'
    return info

def lofter_post_list(url):
    url = re.findall('http.*?\.lofter\.com',url)[0]
    page = 0
    post = []
    while 1==1:
        page += 1
        data = brower.get(url+'/?page='+str(page),headers=headers).text
        post_list = re.findall('href="(https://.*?\.lofter\.com/post.*?/.*?_.*?)"',data)
        if len(post_list) == 0:
            break
        post_list = dic(post_list)
        post = post + post_list
    return post

def lofter_down(data):
    #print('数据分析完毕')
    #创建根文件夹
    save_dir = local_dir+'/'+clean_name(data['title'])
    os.makedirs(save_dir,exist_ok=True)

    #保存元数据为json以便调用
    #print('保存元数据')
    save_json(save_dir+'/entry.json',data)

    #创建下载
    #print('启动媒体数据本地化')
    os.makedirs(save_dir+'/img',exist_ok=True)#创建临时文件夹
    down_img(data['image'],save_dir)
        #修正aria下载图片文件名错误
    #print('修正下载文件名错误')
    down_name = os.listdir(save_dir+'/img')
    for change_name in down_name:
        if 'img%2F' in change_name:
            #捕获错误段
            true_name = re.findall('img%2F.*%2F(.*\....)',change_name)[0]
            os.rename(save_dir+'/img/'+change_name,save_dir+'/img/'+true_name)
    #print('媒体文件下载完毕')

    #html本地化
        # 截取图片文件名
    new_img_list = []
    for url in data['image']:
        img_name = url.split('/').pop()
        new_img_list.append(img_name)
    for num in range(len(new_img_list)):
        data['html'] = data['html'].replace(data['image'][num],'/img/'+new_img_list[num])
    #创建index.html
    if data['html'] != 'null':
        save_txt(save_dir+'/index.html',data['html'])
    if data['txt'] != 'null':
        save_txt(save_dir+'/index.txt',data['txt'])
    #print('索引链接创建完成')
    #print('本地化完成')
    return

def lofter_downs(dl):
    for data in dl:
        lofter_down(data)
    downlist = []
    save_set(downlist)


#清洗文件名
def clean_name(strs):
    strs = re.sub(r'/:<>?/\^|', "",strs)
    # 去除不可见字符
    return strs


def save(name,data):
    with open(name,'w',encoding='utf-8') as f:
        json.dump(data,f)

def save_usual(name,data):
    with open(name,'w',encoding='utf-8') as f:
        f.write(data)


def get(url,header):
    base_data = brower.get(url,headers=header)#拉取网页源码
    return base_data



#初始化
brower = requests.Session()
local_time = time.strftime("%y/%m/%d", time.localtime())
if not os.path.exists('set.json'):
    local_dir = os.getcwd()+'/Download'
    set = {}
    set['download'] = local_dir
    save_setjson()
if os.path.exists('set.json'):
    set = get_setjson()
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
headers_phone = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36'
    }
api_url = 'http://url2api.applinzi.com/' # URL2Article API地址，使用体验版或购买独享资源

#创建下载列表
global downlist
downlist = []

#webui创建
class LofterSaver(App):
    #自定义样式表
    #def __init__(self,*args):
    #    res_path = os.path.join(os.path.dirname(__file__),'res')
    #    super(LofterSaver,self).__init__(*args,static_file_path={'res':res_path})
    def main(self):
        #设置主窗口
        self.tab = gui.Container(width='100%',height='100%',style='background-color: #0465FF')
        self.tab.style['justify-content'] = 'space-around'
        self.tab.style['align-items'] = 'baseline'

        ###################
        #设置main分窗口
        tab_main = gui.VBox(width='100%',height='50%',style='background-color: #82C1FF')
            #设置文本框
        title = gui.Label('Lofter Saver')
        self.text_box = gui.Input(width='30%',height='10%')
        tab_main.append(self.text_box)
            #设置解析按钮
        self.get_buttom = gui.Button(text='解析数据',width='20%',height='10%')
        tab_main.append(self.get_buttom)
            #设置信息展示窗口
        self.tab_infobox = gui.VBox()
        tab_main.append(self.tab_infobox)
        self.tab.append(tab_main,key='主界面')#添加main分窗口

        #设置down分窗口
        self.tab_down = gui.VBox(width='100%',style='background-color: #6089FF')
        self.tab_down_list = gui.VBox(width='95%',style='background-color: #275CF2')

            #设置按钮
        down_buttom = gui.HBox(width='100%',style={"white-space":"pre"})
        self.list_start = gui.Button(text='开始',width='50%',height='10%',style='position:absolute')
        self.list_clean = gui.Button(text='清除',width='50%',height='10%',style='position:absolute')
        down_buttom.append(self.list_start)
        down_buttom.append(self.list_clean)
        self.tab_down.append(down_buttom)
        self.tab_down.append(self.tab_down_list)
        self.tab.append(self.tab_down,key='下载列表')#添加down分窗口

        #设置set分窗口
        tab_set = gui.VBox(width='100%',style='background-color: #22D78A')
        self.tab.append(tab_set,key='设置')#添加set分窗口
        about_title = gui.Label('设置')
        about_downdir_box = gui.HBox()
        about_downdir_title = gui.Label('下载位置：')
        self.about_downdir = gui.Input()
        self.about_downdir.set_value(set['download'])
        self.about_downdir_buttom = gui.Button('刷新路径')
        self.exit = gui.Button("关闭服务",style='background-color: #FF0000')
        about_info = gui.Label('Copyright 2022 LofterSaver 1.1.0 Dev')

        about_downdir_box.append(about_downdir_title)
        about_downdir_box.append(self.about_downdir)
        about_downdir_box.append(self.about_downdir_buttom)
        tab_set.append(about_title)
        tab_set.append(about_downdir_box)
        tab_set.append(self.exit)
        tab_set.append(about_info)
        ##################

        #创建监听事件
        self.get_buttom.onclick.do(self.get_press)#解析链接
        self.list_start.onclick.do(self.down_list_start)#开始下载任务
        self.list_clean.onclick.do(self.down_list_clean)#清空下载列表
        self.about_downdir_buttom.onclick.do(self.set_downdir)#刷新下载路径
        self.exit.onclick.do(self.exit_all)#关闭服务器
        self.down_list()
        return self.tab

    #监听事件
    def down_list(self):#下载列表显示
        downlist=get_set()
        key = 0
        self.tab_down_list.empty()#清空下载列表
        for data in downlist:
            key += 1
            if data == 'null':#跳过占位值
                continue
            box = gui.HBox(width='95%',height='10%')
            title = gui.Label(data['title'])
            delate = gui.Button('删除')
            box.append(title,key='title')
            box.append(delate,key='delate')
            self.tab_down_list.append(box,key=str(key))
            delate.onclick.do(self.down_list_del,str(key))#建立单项任务监听

    def down_list_del(self,emitter,key):#删除单项任务
        try:
            self.tab_down_list.remove_child(self.tab_down_list.children[key])
        except:
            return
        downlist[int(key)-1] = 'null'#建立占位项
        save_set(downlist)

    def get_press(self,emitter,downlist=get_set()):#解析链接
        answer = self.text_box.get_value()
        self.text_box.set_value('')
        if len(re.findall('://.*?\.lofter\.com/post/........_.........',answer)) == 0:
            self.tab_infobox.empty()
            if 'lofter.com' in answer:
                answer_list = lofter_post_list(answer)
                if len(answer_list) != 0:
                    for url in answer_list:
                        info_data = lofter_info(brower.get(url,headers=headers).text)
                        if not info_data in downlist:
                            downlist.append(info_data)
                        downlist = dic(downlist)#去重
                        save_set(downlist)
                    info_title = gui.Label('批量任务')
                    info_num = gui.Label('任务数量：'+str(len(answer_list)))
                    self.tab_infobox.empty()
                    self.tab_infobox.append([info_title,info_num])
                    self.tab_down_list.empty()#清空下载列表
                    key = 0
                    for data in downlist:
                        key += 1
                        if data == 'null':#跳过占位值
                            continue
                        box = gui.HBox(width='95%',height='10%',margin='1px auto')
                        title = gui.Label(data['title'])
                        delate = gui.Button('删除')
                        box.append(title,key='title')
                        box.append(delate,key='delate')
                        self.tab_down_list.append(box,key=str(key))
                        delate.onclick.do(self.down_list_del,str(key))#建立单项任务监听
                    return
            login_txt = gui.Label('链接输入错误')
            self.tab_infobox.append(login_txt)
            return
        if len(re.findall('://.*?\.lofter\.com/post/........_.........',answer)) != 0:
            answer = 'http'+re.findall('://.*?\.lofter\.com/post/........_.........',answer)[0]
        login_txt = gui.Label('加载中。。。。')
        self.tab_infobox.append(login_txt)
        info_data = lofter_info(brower.get(answer,headers=headers).text)#获取数据
        info_title = gui.Label('标题：'+info_data['title'])
        if info_data['image'] == 'null':
            info_img = gui.Label('图片：不存在')
        elif info_data['image'] != 'null':
            info_img = gui.Label('图片：存在')
        if info_data['html'] == 'null':
            info_html = gui.Label('网页正文：不存在')
        elif info_data['html'] != 'null':
            info_html = gui.Label('网页正文：存在')
        self.tab_infobox.empty()
        self.tab_infobox.append([info_title,info_html,info_img])
        downlist=get_set()
        if not info_data in downlist:
            downlist.append(info_data)
        downlist = dic(downlist)#去重
        save_set(downlist)
        self.down_list()

    def down_list_start(self,emitter):#开始下载
        lofter_downs(get_set())
        self.tab_down_list.empty()
        return

    def down_list_clean(self,emitter):#清空下载列表
        self.tab_down_list.empty()
        downlist = []
        save_set(downlist)

    def set_downdir(self,emitter):#刷新下载列表
        answer = self.about_downdir.get_value()
        if answer == set['download']:
            self.about_downdir_buttom.set_text('无需设置')
            return
        if os.path.exists(answer):
            set['download'] = str(answer)
            self.about_downdir_buttom.set_text('设置成功')
            save_setjson()
            return
        self.about_downdir_buttom.set_text('路径不存在')
        set['download'] == os.getcwd()+'/Download'
        save_setjson()
        self.about_downdir.set_value(set['download'])

    def exit_all(self,emitter):#关闭服务器
        self.close()

print('服务启动中。。。')
start(LofterSaver,debug=True,start_browser=False)
