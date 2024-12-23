import time
import re

from loguru import logger
from kivy.lang import Builder

from kivymd.material_resources import dp
from kivymd.app import MDApp
from kivy.core.text import LabelBase
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar.snackbar import MDSnackbar, MDSnackbarButtonContainer, MDSnackbarCloseButton ,MDSnackbarActionButton, MDSnackbarText, MDSnackbarSupportingText, MDSnackbarActionButtonText
from kivymd.uix.list.list import MDListItem, MDListItemSupportingText, MDListItemHeadlineText

class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()

class BaseScreen(MDScreen):
    image_size = StringProperty()

import core
LabelBase.register(name='Roboto',
    fn_regular='SourceHanSansSC-Regular.ttf',
    fn_bold='SourceHanSansSC-Bold.ttf')
 
KV = '''
<BaseMDNavigationItem>

    MDNavigationItemIcon:
        icon: root.icon

    MDNavigationItemLabel:
        text: root.text


<BaseScreen>


MDBoxLayout:
    orientation: "vertical"
    md_bg_color: self.theme_cls.backgroundColor

    MDScreenManager:
        id: screen_manager

        BaseScreen:#主屏幕
            name: "Main Screen"
            MDTextField:
                adaptive_size: True
                multiline: True
                id: urlinput
                mode: "outlined"
                pos_hint: {"center_x": .5, "center_y": .9}
                allow_selection: True#允许选择
                allow_copy: True#允许复制

                MDTextFieldLeadingIcon:
                    icon: "magnify"

                MDTextFieldHelperText:
                    text: "帮助文本"
                    mode: "persistent"

                MDTextFieldTrailingIcon:
                    icon: "information"
            MDButton:
                style: "elevated"
                pos_hint: {"center_x": .5, "center_y": .8}
                on_release: app.test()

                MDButtonIcon:
                    icon: "plus"

                MDButtonText:
                    text: "Elevated"

        BaseScreen:#文章详情屏幕
            name: "Article Screen"
            
            MDBoxLayout:
                orientation: "vertical"
                
                MDTopAppBar:
                    type: "small"
                    size_hint_x: .8
                    pos_hint: {"center_x": .5}
                    
                    MDTopAppBarLeadingButtonContainer:
                        
                        MDActionTopAppBarButton:
                            icon: "arrow-left"
                            on_release: app.on_back()#返回主屏幕
                    
                    MDTopAppBarTitle:
                        text: "详情"
                        pos_hint: {"center_x": .5}
                    
                    MDTopAppBarTrailingButtonContainer:

                        MDActionTopAppBarButton:
                            icon: "download"
                            on_release: app.on_download()

                MDScrollView:#滚动视图
                    do_scroll_x: False#不允许x轴滚动
                    do_scroll_y: True#允许y轴滚动

                    MDBoxLayout:
                        adaptive_height: True#适应高度
                        id: article
                        orientation: "vertical"

                        MDListItem:
                            AsyncImage:  # MDListItemLeadingAvatar
                                id: article_user_img
                                icon: "account"
                            MDListItemHeadlineText:
                                id: article_title
                                text: 'article_user_name'
                            MDListItemSupportingText:
                                id: article_user_name
                                text: 'article_time'

                        MDBoxLayout:
                            adaptive_height: True
                            MDLabel:
                                adaptive_height: True#适应高度
                                id: article_content
                                text: "article_content"

        BaseScreen:#作者详情屏幕
            name: "Author Screen"
            #TODO

        BaseScreen:
            name: "Progress Screen"
            MDScrollView:#滚动视图
                do_scroll_x: False#不允许x轴滚动
                do_scroll_y: True#允许y轴滚动
                MDBoxLayout:
                    id: local_articles_list
                    orientation: "vertical"


        BaseScreen:#设置屏幕
            name: "Setting Screen"
            MDTopAppBar:
                type: "small"
                size_hint_x: .8
                pos_hint: {"center_x": .5, "center_y": .5}

                MDTopAppBarTitle:
                    text: "设置"
                    pos_hint: {"center_x": .5}

        



    MDNavigationBar:
        on_switch_tabs: app.on_switch_tabs(*args)

        BaseMDNavigationItem
            icon: "gmail"
            text: "Main Screen"
            active: True
        BaseMDNavigationItem
            icon: "article"
            text: "Article Screen"
        BaseMDNavigationItem
            icon: "progress-clock"
            text: "Progress Screen"

        BaseMDNavigationItem
            text: "Setting Screen"


    

    MDLinearProgressIndicator:
        type: "determinate"
        id: progress
        size_hint_x: .5
        size_hint_y: None
        height: dp(5)#设置进度条厚度
        value: 0
        max: 100
        radius: self.height / 2#用来给进度条添加圆角
        pos_hint: {'center_x': .5, 'center_y': .4}

'''

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
        logger.debug('正在解析第'+str(page)+'页')
        #out.toast('正在解析第'+str(page)+'页',position='left', color='info', duration=1)#弹出提示
        post_list = core.dic(post_list)
        if len(core.dic(post + post_list)) - len(post) == 0:
            break
        post = core.dic(post + post_list)
        logger.debug('本页提取'+str(len(post_list))+'个文章')
        logger.info('已提取'+str(len(post))+'个文章')
        #out.toast('已提取'+str(len(post))+'个文章',position='left', color='info', duration=1)#弹出提示
    print('共提取'+str(len(post))+'个文章')
    #out.toast('已提取'+str(len(post))+'个文章',position='left', color='success', duration=0)#弹出提示
    return post

def lofter_print(self,answer):
    '''
    打印文章信息
    '''
    logger.debug('作者 "'+answer['writer']['name']+'"')
    self.root.ids.article_user_name.text = answer['writer']['name']
    self.root.ids.article_user_img.source = answer['writer']['img']
    self.root.ids.article_title.text = answer['title']
    self.root.ids.article_content.text = answer['txt']
    logger.debug('文章覆盖详情')

def start_url(url):
    if 'lofter' in url:#如果为lofter地址
        if '/post/' not in url:#尝试批量获取
            list = lofter_post_list(url)
            print(list)
            #lofter_list_print(list)#显示列表
            #清除旧显示内容
            #out.clear('info')
            return
        answer = core.lofter_request_info(url)
        if answer == 'error':
            logger.warning('解析失败')
            return
        #显示内容
        #lofter_print(answer)
        #清除旧显示内容
        #out.clear('info')

        return answer

def snakebar(self,msg):
    '''
    显示提示消息
    '''
    MDSnackbar(
        MDSnackbarSupportingText(
            text=msg,
        ),
        y = dp(15),
        orientation="horizontal",
        pos_hint={"center_x": 0.5},
        size_hint_x=0.5,
        background_color=self.theme_cls.onPrimaryContainerColor,
    ).open()

article_data = {}#全局变量
#刷新本地文章列表
def refresh_local_articles(self):
    def add_list(self,dir_name):
        self.root.ids.local_articles_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(
                        text=str(dir_name),
                    ),
                    MDListItemSupportingText(
                        text="Supporting text",
        ),
        id=i.stem
                )
            )
    local_articles = core.get_local_articles('D:\code\Lofter-Saver\Download')
    for i in local_articles:
        #检查页面中有无文章
        if len(self.root.ids.local_articles_list.children) == 0:
            add_list(self,i.stem)
            logger.info('本地列表添加文章：'+i.stem)
        #检查是否存在重复文章
        for o in self.root.ids.local_articles_list.children:
            if o.id == i.stem:
                continue
            else:
                add_list(self,i.stem)
                logger.info('本地列表添加文章：'+i.stem)

    return
class Main(MDApp):
    urlinput = ObjectProperty(None)#url输入框
    article = ObjectProperty(None)#文章显示小部件
    article_user_name = ObjectProperty(None)#文章作者名称
    article_user_title = ObjectProperty(None)#文章标题
    article_user_img = ObjectProperty(None)#文章作者头像
    article_content = ObjectProperty(None)#文章内容
    local_articles_list = ObjectProperty(None)#本地文章列表
    def test(self):
        global article_data
        answer = start_url(self.root.ids.urlinput.text)
        lofter_print(self,answer)
        article_data = answer


    def on_download(self):#下载文章
        global article_data
        core.down(article_data,'/')
        logger.info('"'+article_data['title']+'" 下载成功')
        snakebar(self,'"'+article_data['title']+'" 下载成功')

    def on_back(self):#返回主屏幕
        self.root.ids.screen_manager.current = 'Main Screen'

    def on_switch_tabs(
            self,
            bar: MDNavigationBar,
            item: MDNavigationItem,
            item_icon: str,
            item_text: str,
        ):#切换屏幕
            self.root.ids.screen_manager.current = item_text
            if item_text == 'Progress Screen':
                refresh_local_articles(self)#刷新本地列表
    def build(self):
        
        self.theme_cls.primary_palette = "Green"
        return Builder.load_string(KV)


Main().run()