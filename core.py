import requests
from readability import Document
from bs4 import BeautifulSoup
from tqdm import tqdm
import wget
import unicodedata#标准编码库

from pathlib import Path
import re
import os

from datetime import datetime
import time
import json
import pickle#数据持久化
list = []
fin_list = []

brower = requests.Session() #创建浏览器
headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.20 Safari/537.36'
    }
headers_phone = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36'
    }
api_url = 'http://url2api.applinzi.com/' # URL2Article API地址，使用体验版或购买独享资源

api_headers = {'User-Agent': 'LOFTER-Android 7.3.4 (PRA-AL00X; Android 8.0.0; null) WIFI'}
api_cookies = {'Cookie': 'usertrack=dZPgEWPiVMNF6YfwJEIHAg==; NEWTOKEN=ZGUyN2NjOTE1YzE2ZmIwOTM0ZGU5MTIwYjJkZjBhNDJkMDI3YTliNGE4M2ZhMjkxYmY3ODZkN2VkNWRhZTBkNDE1Y2NkNDg4ZDUyMDAzZWNmNWUyMjgwNWY5NTQ2MGZm; NTESwebSI=DFD9B345542ECECF843D7DC7D99313F2.lofter-tomcat-docker-lftpro-3-avkys-cd6be-774f69457-rggg6-8080'}

#get
def gets(url):
    try:
        #cj = {i.split("=")[0]:i.split("=")[1] for i in cookies.split(";")}
        response = brower.get(url=url,headers=headers,timeout=5)
        if response.status_code == 200:
            return response.text
        if response.status_code == 404:
            print('网址不存在')
            return 'null'
        print(response.status_code)
        print(url+'访问出错')
        time.sleep(1)
        gets(url)
    except:
        print(url+'访问崩溃,请检查网络')
        time.sleep(1)
        gets(url)

def api_post(url):
    try:
        #cj = {i.split("=")[0]:i.split("=")[1] for i in api_cookies.split(";")}
        response = brower.post(url=url,headers=api_headers,cookies=api_cookies,timeout=5)
        if response.status_code == 200:
            return response
        if response.status_code == 404:
            print('网址不存在')
            return 'null'
        print(response)
        print(url+'访问出错')
        time.sleep(1)
        gets(url)
    except:
        print(url+'访问崩溃,请检查网络')
        time.sleep(1)
        gets(url)

#清洗文件名
def clean_name(strs):
    strs = unicodedata.normalize('NFKD',strs)
    strs = re.sub(r'/<>/\^|@&', "",strs)
    strs = strs.replace('@','')
    strs = strs.replace('&','')
    strs = strs.replace(':','：')
    strs = strs.replace('?','？')
    strs = strs.replace('|',' ')
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

#获取与修改下载列表
def downlist(set='null'):
    global list
    if set == 'null':
        return list
        if os.path.exists('downlist.obj') and os.path.getsize('downlist.obj') > 0:
            with open('downlist.obj','rb') as f:
                list = pickle.load(f)
            return list
        else :
            with open('downlist.obj','wb') as f:
                pickle.dump([],f)
        return []
    else:
        list = set
        with open('downlist.obj','wb') as f:
            pickle.dump(set,f)

#获取与修改完成列表
def finlist(set='null'):
    global fin_list
    if set == 'null':
        return fin_list
        if os.path.exists('finlist.obj') and os.path.getsize('finlist.obj') > 0:
            with open('finlist.obj','rb') as f:
                list = pickle.load(f)
            return list
        else :
            with open('finlist.obj','wb') as f:
                pickle.dump([],f)
        return []
    else:
        fin_list = set
        with open('finlist.obj','wb') as f:
            pickle.dump(set,f)

#删除下载任务
def del_downlist(info):
    old_downlist = downlist()
    new_downlist = []
    for a in old_downlist:#查找一致id的内容并排除
        if a['targetblogid'] != info['targetblogid'] or a['postid'] != info['postid']:
            new_downlist.append(a)
    downlist(new_downlist)#重新写入下载列表
    return

def get_set():
    with open('set.json','r') as f:
        set = json.load(f)
    return set

def save_set(set):
    with open('set.json','w') as f:
        json.dump(set,f)


#readability接口解析
def clean_1(data): #获取网站正文文本
    try:
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
        txt = txt.replace('&nbsp;','')
        #创个字典存放数据
        fine = {}
        fine['title'] = title
        fine['html'] = html
        fine['txt'] = txt
    except:
        #创个字典存放数据
        fine = {}
        fine['title'] = 'null'
        fine['html'] = 'null'
        fine['txt'] = 'null'
        return fine
    return fine

#url2io接口
def clean_2(url):
    token = 'MeTlIPmSRjmWgaNa9GzDAw' # 开发者 token, 注册后可得，注意保密
    fields = ','.join(['next','txt']) # 可选字段# HTTP Get
    result = brower.get(api_url+'article?token='+token+'&url='+url+'&fields='+fields).json()
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
    save_dir = str(save_dir)
    sep = '\n'
    if img == 'null':
        return
    with open(Path(save_dir+'/url.txt'),'w') as f:
        f.write(sep.join(img))
    for url in tqdm(img,desc='图片下载中：',unit='img'):
        wget.download(url,save_dir)
    #os.system('aria2c --quiet true -j 10 --continue=true --dir="'+str(Path(save_dir))+'" -i "'+str(Path(save_dir+'/url.txt'))+'"')
    return

#lofter文章信息获取
def lofter_info(data):
    try:
        html_txt = data
        sp = BeautifulSoup(data,'lxml')
        #标题提取
        title_data = sp.find_all(name="meta")
        title = 'null'
        for data in title_data:
            if "Description" in str(data):
                title_1 = data['content']
                break
        title_2 = re.findall("<title>(.*?)</title>",html_txt)[0]
        if len(title_1) > len(title_2):
            title = title_2
        else:
            title = title_1
        if len(title) >= 60:
            title = str(title)[0:60]
        #图片提取
        image_data = sp.find_all(imggroup="gal")
        if len(image_data) != 0:
            image_url = re.findall('src="(https://.*?g)\?',str(image_data))
        #整理数据
        info = {}
        info['html'] = html_txt
        info['title'] = title
        if len(image_data) != 0:
            info['image'] = dic(image_url)
        if len(image_data) == 0:
            info['image'] = 'null'
    except:
        try:
            info = {}
            info['html'] = data
            info['title'] = title
            if len(image_data) != 0:
                info['image'] = dic(image_url)
            if len(image_data) == 0:
                info['image'] = 'null'
            print(info['title'])
            return info
        except:
            info = {}
            info['html'] = 'null'
            info['title'] = 'null'
            info['image'] = 'null'
            print(info['title'])
            return info
    print(info['title'])
    return info

#lofter客户端api解析引擎
def lofter_api(targetblogid:int,postid:int) -> dict:
    """
    输入targetblogid,blogid
    调用安卓客户端oldapi

    status = api状态
    msg = 状态信息
    title = 文章标题
    writer name = 作者名
    writer img = 作者头图
    info = 文章内容
    img = 图片链接
    """

    json_answer = api_post('https://api.lofter.com/oldapi/post/detail.api?product=lofter-android-7.3.4&targetblogid='+str(targetblogid)+'&supportposttypes=1,2,3,4,5,6&offset=0&postdigestnew=1&postid='+str(postid)+'&blogId='+str(targetblogid)+'&checkpwd=1&needgetpoststat=1').json()
    info = {}
    info['targetblogid'] = targetblogid
    info['postid'] = postid
    info['status'] = json_answer['meta']['status']#api状态
    info['msg'] = json_answer['meta']['msg']#状态信息
    #判断作品状态
    if str(info['status']) == '4202':#作品被删除
        print(info['msg'])
        info['status'] = 404
        info['title'] = '错误'
        info['writer'] = {}
        info['writer']['name'] = '错误'#作者名
        info['writer']['img'] = ''#作者头图
        info['info'] = ''#文章内容
        info['type'] = 1#文章类型 1为文档 2为含有图片 3为音乐（？
        info['img'] = []
        return info

    try:#某些特殊玩意根本没有标题参数
        info['title'] = json_answer['response']['posts'][0]['post']['title']#文章标题
    except:
        info['title'] = datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S %f')
    if info['title'] == '':
        info['title'] = datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S %f')
    info['writer'] = {}
    info['writer']['name'] = json_answer['response']['posts'][0]['post']['blogInfo']['blogNickName']#作者名
    info['writer']['img'] = json_answer['response']['posts'][0]['post']['blogInfo']['bigAvaImg']#作者头图
    info['info'] = json_answer['response']['posts'][0]['post']['content']#文章内容
    info['type'] = json_answer['response']['posts'][0]['post']['type']#文章类型 1为文档 2为含有图片 3为音乐（？
    info['img'] = []
    if info['type'] == 2:
        for a in json.loads(json_answer['response']['posts'][0]['post']['photoLinks']):#图片链接
            info['img'].append(a['raw'])
        #os.makedirs(Path('bug'),exist_ok=True)#创建临时文件夹
        #save_json(str(Path('bug/'+str(targetblogid)+'_'+str(postid)+'.json')),json_answer)
        #print('出现错误')
    return info

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
        data = gets(post_url)
        if data == 'null':
            return 'null'
        kk = re.compile('"(https://.*?\.lofter\.com/post/.*?_.*?)"')
        post_list = kk.findall(data)
        print('正在解析第'+str(page)+'页')
        post_list = dic(post_list)
        if len(dic(post + post_list)) - len(post) == 0:
            break
        post = dic(post + post_list)
        print('本页提取'+str(len(post_list))+'个文章')
        print('已提取'+str(len(post))+'个文章')
    print('共提取'+str(len(post))+'个文章')
    return post

def down(data,local_dir):
    text = clean_1(data['html']) #清洗文本
    #检查是否有有效文本信息
    test = text['txt'].replace('\n','')
    if test == '':
        test = 'null'
    data['txt'] = text['txt']
    if data['title'] == 'null':
        return
    print('数据分析完毕')
    #创建根文件夹
    save_dir =str(Path(str(local_dir)+'/'+clean_name(data['title'])).resolve())
    a = 0
    if Path(save_dir).exists() :
        while 1==1:
            a += 1
            if Path(save_dir+str(a)).exists() :
                continue
            save_dir = save_dir+str(a)
            break
    os.makedirs(save_dir,exist_ok=True)

    #保存元数据为json以便调用
    print('保存元数据')
    save_json(Path(save_dir+'/entry.json'),data)

    #创建下载
    if len(data['image']) != 0:
        print('启动媒体数据本地化')
        os.makedirs(Path(save_dir+'/img'),exist_ok=True)#创建临时文件夹
        down_img(data['image'],Path(save_dir+'/img'))
            #修正aria下载图片文件名错误
        print('修正下载文件名错误')
        down_name = os.listdir(Path(save_dir+'/img'))
        for change_name in down_name:
            if 'img%2F' in change_name:
                #捕获错误段
                true_name = change_name.replace('%2F','')
                #true_name = true_name[3:]
                os.rename(Path(save_dir+'/img/'+change_name),Path(save_dir+'/img/'+true_name))
        print('媒体文件下载完毕')

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
        save_txt(Path(save_dir+'/index.html'),data['html'])
    if data['txt'] != 'null':
        save_txt(Path(save_dir+'/index.txt'),data['txt'])
    print('索引链接创建完成')
    print('本地化完成')
    return

