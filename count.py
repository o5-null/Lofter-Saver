import jionlp
import jieba
import thulac
from goose3 import Goose
from goose3.text import StopWordsChinese
thu = thulac.thulac(seg_only=True,filt=True)
#g = Goose({'stopwords_class': StopWordsChinese})
with open('《一世之尊》.txt','r',encoding='UTF-8') as f:
    txt = f.read()
#res = g.extract(raw_html=txt).cleaned_text
#res = jionlp.clean_text(txt)
#words = thu.cut('HULAC（THU Lexical Analyzer for Chinese）由清华大学自然语言处理与社会人文计算实验室研制推出的一套中文词法分析工具包，具有中文分词和词性标注功能。THULAC具有如下几个特点')
#print(res)
stopwords = jionlp.stopwords_loader()
words  = thu.cut(txt)
counts = {}  
for word in words:  
    word = word[0]
    #不在停用词表中  
    if word not in stopwords:  
        #不统计字数为一的词  
        if len(word) == 1:  
            continue  
        else:  
            counts[word] = counts.get(word,0) + 1  
items = list(counts.items())  
items.sort(key=lambda x:x[1], reverse=True)   
for i in range(len(words)):  
    word, count = items[i]  
    print ("{:<10}{:>7}".format(word, count))