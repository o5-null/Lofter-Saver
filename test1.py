import core
import requests
import base64
import datetime

def get_formatted_datetime(custom_time=None):
    # 获取当前时间或用户指定的时间
    if custom_time:
        dt = datetime.datetime.strptime(custom_time, '%Y-%m-%d %H:%M:%S')
    else:
        dt = datetime.datetime.now()

    # 自定义星期几的映射
    weekday_abbr = {
        0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu',
        4: 'Fri', 5: 'Sat', 6: 'Sun'
    }

    # 格式化日期时间为所需格式
    formatted_datetime = f"{weekday_abbr[dt.weekday()]}, {dt.day:02d} {dt.strftime('%b')} {dt.year} {dt.strftime('%H:%M:%S')} GMT"
    return formatted_datetime

a = core.lofter_writer_api(517076566,0,20)
print(a)
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

data = {"supportposttypes": "1,2,3,4,5,6",
        ##"blogdomain": blogname,#blogname和targetblogid有一个就行
        "targetblogid": 517076566,
        "offset": 0,#偏移量，这次获取的作品的起始位置
        "postdigestnew": 1,
        "returnData": 1,
        "limit": 20,#获取作品数量
        "openFansVipPlan": 0,
        "checkpwd": 1,
        "needgetpoststat": 1,
        "method": "getPostLists"#指示为获取作品列表
    }

answer = requests.post('https://api.lofter.com/v2.0/blogHomePage.api?product=lofter-android-8.1.0', headers=headers, data=data)
print(answer.text)

