# -*- coding: utf-8-*-
import sys


# print 'System Default Encoding:',sys.getdefaultencoding()
# reload(sys)
# sys.setdefaultencoding('gbk')   #Tommy: this make IPthon display chinese OK.

import win32com
from win32com.client import Dispatch, constants

#模板文件保存路径，此处使用的是绝对路径，相对路径未测试过
template_path = "d:\\github\\apps\\MyPython\\ReplaceWordInDoc\\input\\template.docx"

#另存文件路径，需要提前建好文件夹，不然会出错
store_path = "d:\\github\\apps\\MyPython\\ReplaceWordInDoc\\output\\"
#模板中需要被替换的文本。	u''中的u表示unicode字符，用于中文支持
NewStr = u'孙悟空'

#启动word
w = win32com.client.DispatchEx('Word.Application')
print 'w=', w
# 或者使用下面的方法，使用启动独立的进程：
# w = win32com.client.DispatchEx('Word.Application')

# 后台运行，不显示，不警告
w.Visible = False
w.DisplayAlerts = 0

# 打开新的文件
doc = w.Documents.Open(template_path)
# worddoc = w.Documents.Add() # 创建新的文档
print 'doc=', doc

if doc == None:
    print 'Open', template_path, 'Failed !'
    print template_path
    exit()


# 插入文字
#myRange = doc.Range(0,0) 
#这句话让你获取的是doc的最前面位置,如果想要获取到其他位置，就要改变Range中的参数，两个参数分别代表起始点，结束点。。。
#myRange.InsertBefore('Hello from Python!')
 
# 正文文字替换
w.Selection.Find.ClearFormatting() 
w.Selection.Find.Replacement.ClearFormatting()

#名单
namelist = [
u"张三", 
u'李四', 
u'王五',
u'Mr. Gatsby',
u'Charles',
u'Chasel',
u'Chester',
u'Christ',
u'Christian',
u'Christopher',
u'Clare',
u'Clarence',
u'Clark',
u'Claude',
u'Clement',
]

#迭代替换名字，并以名字为名另存文件
for name in namelist:
    print 10*'*', name, 10*'*'
    OldStr, NewStr = NewStr, name
    #print OldStr, NewStr
    w.Selection.Find.Text = OldStr
    w.Selection.Find.Replacement.Text = NewStr
    w.Selection.Find.Execute(OldStr, False, False, False, False, False, True, 1, True, NewStr, 2)
    doc.SaveAs(store_path + u"输出文件名_"+ name +".doc")
    #直接打印，未测试
    #doc.PrintOut()		

doc.Close()
#w.Documents.Close()
w.Quit()


