import requests
from readability import Document
from bs4 import BeautifulSoup
from tqdm import tqdm
import wget
import unicodedata#标准编码库

from pathlib import Path
import re
import os

from loguru import logger#日志记录
from datetime import datetime
import time
import json
import pickle#数据持久化
list = []
fin_list = []


brower = requests.Session() #创建浏览器
headers = {
 #'x-device':'hXriTGNOmtmur+Tu/1D6+WaUESjo5Ccod12fMWkJd2EdseYwrN8mVvzdHjbV9Tr7',
 #'lofproduct':'lofter-android-8.1.0',
 'user-agent':'LOFTER-Android 8.1.0 (V2245A; Android 12; null) WIFI',
 #'authorization':'ThirdParty LOFTER#ed5ffb1661fa1e40804f537a4c8c3cf2a90f965e442a0ba5ad6437cc881d21d313fb721ef255c5c4523cbacf706ed6d026837f1229a486bd8f6a1b6a937d0188747a787ef97032392c822061e489dce4',
 #'market':'LOFTER',
 #'deviceid':'0447d047333e0441',
 #'dadeviceid':'2b9c36bce0eb3b34f4a04ad085ee5f1979d73831',
 #'androidid':'0447d047333e0441',
 #'x-reqid':'Q632K1S9',
 'accept-encoding':'br,gzip',
 'content-type':'application/x-www-form-urlencoded; charset=utf-8',
 #'content-length':'210',
 'cookie':'NTESwebSI=4819B9242EE3F2EF1A896B3B9B6F59AA.lofter-tomcat-docker-lftpro-3-avkys-13dx0-74c7c4bd9d-tcv28-8080'}

headers_phone = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; PRA-AL00X Build/HONORPRA-AL00X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36'
    }
api_url = 'http://url2api.applinzi.com/' # URL2Article API地址，使用体验版或购买独享资源

api_headers = {'User-Agent': 'LOFTER-Android 7.3.4 (PRA-AL00X; Android 8.0.0; null) WIFI'}
api_cookies = {'Cookie': 'NTESwebSI=D557F7AC800EC08EEEC2A123A2E0CF70.lofter-tomcat-docker-lftpro-3-avkys-13dx0-74c7c4bd9d-7g7pp-8080; Path=/; HttpOnly'}
content_type = "application/x-www-form-urlencoded; charset=utf-8"
product = 'lofter-android-8.1.1'
#get
def gets(url):
    try:
        #cj = {i.split("=")[0]:i.split("=")[1] for i in cookies.split(";")}
        response = brower.get(url=url,headers=headers,timeout=5)
        if response.status_code == 200:
            return response.text
        if response.status_code == 404:
            logger.warning('网址不存在')
            return 'null'
        print(response.status_code)
        logger.warning(url+'访问出错')
        time.sleep(1)
        gets(url)
    except:
        logger.warning(url+'访问崩溃,请检查网络')
        time.sleep(1)
        gets(url)

def get_cookies(url):
    '''
    需要登陆才能请求的api
    '''
    try:
        #cj = {i.split("=")[0]:i.split("=")[1] for i in api_cookies.split(";")}
        response = brower.post(url=url,cookies=api_cookies,headers=headers,timeout=5)
        if response.status_code == 200:
            return response
        if response.status_code == 404:
            logger.warning('网址不存在')
            return 'null'
        print(response)
        logger.warning(url+'访问出错')
        time.sleep(1)
        get_cookies(url)
    except:
        logger.warning(url+'访问崩溃,请检查网络')
        time.sleep(1)
        get_cookies(url)

def post_cookies(url,data):
    '''
    需要登陆带参数才能请求的api
    '''
    try:
        #cj = {i.split("=")[0]:i.split("=")[1] for i in api_cookies.split(";")}
        response = brower.post(url=url,headers=headers,data=data,timeout=5)
        if response.status_code == 200:
            return response
        if response.status_code == 404:
            logger.warning('网址不存在')
            return 'null'
        print(response)
        logger.warning(url+'访问出错')
        time.sleep(1)
        post_cookies(url)
    except:
        logger.warning(url+'访问崩溃,请检查网络')
        time.sleep(1)
        post_cookies(url,data)

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
    """
    去重
    """
    new_list = []#创建临时列表
    for a in info:
        if a == 'null':
            continue
        if not a in new_list:
            new_list.append(a)
    return new_list

def get_local_articles(localdir:str):
    """
    从本地读取文章
    """
    local_articles = []
    p = Path(localdir).resolve()
    for child in p.iterdir():
        local_articles.append(child)
    logger.debug('本地文章数量：'+str(len(local_articles)))
    print(local_articles)
    return local_articles

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

def clean_html(data):
    #获取txt格式
    txt = data.replace('</p>','')#doc.summary()为提取的网页正文但包含html控制符，这一步是替换换行符
    txt = re.sub(r'</?\w+[^>]*>', '', txt)      #这一步是去掉<****>内的内容
    txt = txt.replace('&nbsp;','')
    logger.debug('清理html完成')
    return txt

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
    writer blogname = 作者名
    writer homepageurl = 作者主页
    writer idlocation = 作者ip地址
    info = 文章内容
    type = 文章类型 1为文档 2为含有图片 3为音乐（？
    img = 图片链接
    publishtime = 发布时间
    taglist = 文章标签
    hot = 文章热度
    like = 文章点赞数
    txt = 纯文本

    """

    json_answer = get_cookies('https://api.lofter.com/oldapi/post/detail.api?product=lofter-android-8.1.0&targetblogid='+str(targetblogid)+'&supportposttypes=1,2,3,4,5,6&offset=0&postdigestnew=1&postid='+str(postid)+'&blogId='+str(targetblogid)+'&checkpwd=1&needgetpoststat=1').json()
    info = {}
    info['targetblogid'] = targetblogid
    info['postid'] = postid
    info['status'] = json_answer['meta']['status']#api状态
    info['msg'] = json_answer['meta']['msg']#状态信息
    #判断作品状态
    if str(info['status']) == '4202':#作品被删除
        logger.warning(info['msg'])
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
    info['writer']['nickname'] = json_answer['response']['posts'][0]['post']['blogInfo']['blogNickName']#作者昵称
    info['writer']['img'] = json_answer['response']['posts'][0]['post']['blogInfo']['bigAvaImg']#作者头图
    info['writer']['blogname'] = json_answer['response']['posts'][0]['post']['blogInfo']['blogName']#作者名
    info['writer']['homepageurl'] = json_answer['response']['posts'][0]['post']['blogInfo']['homePageUrl']#作者主页
    info['writer']['idlocation'] = json_answer['response']['posts'][0]['post']['bpostCollection']['ipLocation']#作者ip地址
    info['info'] = json_answer['response']['posts'][0]['post']['content']#文章内容
    info['type'] = json_answer['response']['posts'][0]['post']['type']#文章类型 1为文档 2为含有图片 3为音乐（？
    info['img'] = []
    info['publishtime'] = json_answer['response']['posts'][0]['post']['publishTime']#发布时间
    info['taglist'] = json_answer['response']['posts'][0]['post']['tagList']#文章标签
    info['hot'] = json_answer['response']['posts'][0]['post']['postCount']['postHot']#文章热度
    info['like'] = json_answer['response']['posts'][0]['post']['postCount']['favoriteCount']#文章点赞数
    info['txt'] = clean_html(info['info'])#txt
    if info['type'] == 2:
        for a in json.loads(json_answer['response']['posts'][0]['post']['photoLinks']):#图片链接%
            info['img'].append(a['raw'])
        #os.makedirs(Path('bug'),exist_ok=True)#创建临时文件夹
        #save_json(str(Path('bug/'+str(targetblogid)+'_'+str(postid)+'.json')),json_answer)
        #print('出现错误')
    return info

#获取作者信息
def lofter_writer_info_api(targetblogid):
    data = {"supportposttypes": "1,2,3,4,5,6",
        ##"blogdomain": blogname,#blogname和targetblogid有一个就行
        "targetblogid": targetblogid,
        #"offset": offset,#偏移量，这次获取的作品的起始位置
        #"postdigestnew": 1,
        "returnData": 1,
        #"limit": limit,#获取作品数量
        #"openFansVipPlan": 0,
        "checkpwd": 1,
        "needgetpoststat": 1,
        "method": "getBlogInfoDetail"#指示为获取作者信息
    }
    json_answer = post_cookies('https://api.lofter.com/v2.0/blogHomePage.api?product=lofter-android-8.1.0',data).json()
    return json_answer

#获取作者文章列表
def lofter_writer_list_api(targetblogid,offset:int,limit:int):
    '''
    targetblogid:主页id
    offset:偏移量，这次获取的作品的起始位置
    limit:获取作品数量

    返回参数：
    status = api状态
    msg = 状态信息
    archives = 每月文章数量
    posts = 文章列表
    toppost = 置顶文章
    '''
    data = {"supportposttypes": "1,2,3,4,5,6",
        ##"blogdomain": blogname,#blogname和targetblogid有一个就行
        "targetblogid": targetblogid,
        "offset": offset,#偏移量，这次获取的作品的起始位置
        "postdigestnew": 1,
        "returnData": 1,
        "limit": limit,#获取作品数量
        "openFansVipPlan": 0,
        "checkpwd": 1,
        "needgetpoststat": 1,
        "method": "getPostLists"#指示为获取作品列表
    }
    json_answer = post_cookies('https://api.lofter.com/v2.0/blogHomePage.api?product=lofter-android-8.1.0',data).json()
    info = {}
    info['status'] = json_answer['meta']['status']#api状态
    info['msg'] = json_answer['meta']['msg']#状态信息
    info['archives'] = json_answer['response']['archives']#每月文章数量
    info['posts'] = json_answer['response']['posts']#文章列表
    info['toppost'] = json_answer['response']['topPost']#置顶文章

    logger.debug('获取文章列表:'+str(targetblogid)+', offset:'+str(offset)+', limit:'+str(limit))

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
    text = data['txt']
    #检查是否有有效文本信息
    test = text.replace('\n','')
    if test == '':
        test = 'null'
    data['txt'] = test
    if data['title'] == 'null':
        return
    logger.debug('数据分析完毕')
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

    #创建下载
    if len(data['img']) != 0:
        logger.debug('启动媒体数据本地化')
        os.makedirs(Path(save_dir+'/img'),exist_ok=True)#创建临时文件夹
        down_img(data['img'],Path(save_dir+'/img'))
            #修正aria下载图片文件名错误
        logger.debug('修正下载文件名错误')
        down_name = os.listdir(Path(save_dir+'/img'))
        for change_name in down_name:
            if 'img%2F' in change_name:
                #捕获错误段
                true_name = change_name.replace('%2F','')
                #true_name = true_name[3:]
                os.rename(Path(save_dir+'/img/'+change_name),Path(save_dir+'/img/'+true_name))
        logger.debug('媒体文件下载完毕')

    #html本地化
        # 截取图片文件名
    new_img_list = []
    for url in data['img']:
        img_name = url.split('/').pop()
        new_img_list.append(img_name)
    for num in range(len(new_img_list)):
        data['info'] = data['info'].replace(data['img'][num],'/img/'+new_img_list[num])
    #创建index.html
    if data['info'] != 'null':
        save_txt(Path(save_dir+'/index.html'),data['info'])
    if data['txt'] != 'null':
        save_txt(Path(save_dir+'/index.txt'),data['txt'])
    logger.debug('索引链接创建完成')

    #保存元数据为json以便调用
    logger.debug('保存元数据')
    data.pop('info')#删除html内容，防止占用过多空间
    data.pop('txt')#删除txt内容，防止占用过多空间
    save_json(Path(save_dir+'/entry.json'),data)
    logger.debug('本地化完成')
    return

def lofter_request_info(url):
    #格式化链接
    logger.debug('发送请求 '+url)
    id = re.findall('/post/(.*?_.*)',url)[0]
    id = id.split('_')
    targetblogid = int(id[0],16)
    blogid = int(id[1],16)
    #发送请求
    logger.debug('targetblogid '+str(targetblogid))
    logger.debug('blobid '+str(blogid))
    answer = lofter_api(targetblogid,blogid)
    if answer['status'] != 200:#如果返回不正常
        #弹出错误弹窗
        return 'error'
    return answer
    
