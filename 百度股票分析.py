#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/25 12:18
# @Author  : Yu
# @Site    : 
# @File    : 百度股票分析.py
import requests
import time
from lxml import etree,html
from bs4 import BeautifulSoup
import threading
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import queue
import jieba
import re
import sys
import random
header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
class Socket:
    pass
#从数据库返回一个类型跟代码字段的字典
def from_data():
    dic={}
    sql='select sz_sh,sock from socket'
    print("请稍等，正在读取数据库内容....")
    data=pd.read_sql(sql,con)
    datas=pd.DataFrame(data).values
    #分别利用pandas分割矩阵得到两个列表
    so_type=datas[:,0]
    code=datas[:,1]
    print("数据库读取完毕....")
    #code对应字典
    for i in range(len(code)):
        dic[code[i]]=so_type[i]
    return dic


#构建url队列
def creat_url(dict1):
    #构建队列为多线程做准备
    #由于有的url没有用这里创建临时列表用于清洗
    linshi_list=[]
    Q=queue.Queue()
    print("构建队列中...")
    for code in dict1:
        url='https://gupiao.baidu.com/stock/'+dict1[code]+code+'.html'
        linshi_list.append(url)
    print('获取的总url数量为%s '%len(linshi_list))
    #规定一个爬取区间以为前面有一部分url没用 懒得再测试哪些没用
    while True:
        x = int(input('哪个url开始爬取(最小为0)：'))
        y = int(input('哪个url结束爬取(最大为4573)：'))
        if x < 0 or y > 4573 or x>y:
            print('区间输入出错，请重新输入....')
        else:
            break

    for need in linshi_list[x:y]:
        Q.put(need)
    print('队列创建完成，返回队列...')
    return Q


#获取和解析源代码
def parser_html(url):
    #存储临时数据的列表

    current_list=[]
    try:
        r=requests.get(url,headers=header)
        r.encoding=r.apparent_encoding
        r.raise_for_status()
        if r.status_code==200:
            print("网页请求成功...")
    except:
        print("网页请求出错")
    #需要的参数
    ET=etree.HTML(r.text)
    #股票名字 re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]+'用于过滤有效字符串
    try:
        name = ET.xpath('/html/body/div/div[2]/div/h1/a/text()')[0]
    except:
        print("url:%s无效,继续下一个url请求" % r.url)
        #exit()推出当前线程
        exit()
    name=re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',name)[0]
    # tody
    #今开
    try:
        tody_open = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[1]/dd/text()')[0]

        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',tody_open)[0])
        #成交量
        volume = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[2]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',volume)[0])
        #最高
        higest = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[3]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',higest)[0])
        #涨停
        harden = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[4]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',harden)[0])
        #内盘
        i_dish = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[5]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',i_dish)[0])
        #成交额
        turnover = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[6]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',turnover)[0])
        #委比
        appoint_than = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[7]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',appoint_than)[0])
        #流通市值
        current_market = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[8]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',current_market)[0])
        #市盈率
        radio = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[9]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',radio)[0])
        #每股收益
        per_get = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[10]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',per_get)[0])
        #总股本
        total_equity = ET.xpath('/html/body/div/div[2]/div/div[2]/div[1]/dl[11]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',total_equity)[0])
        #yestody
        #昨日收益
        this_charge = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[1]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',this_charge)[0])
        #换手率
        Turnover_rate = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[2]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',Turnover_rate)[0])
        #最低
        lowest = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[3]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',lowest)[0])
        #涨停
        y_harden = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[4]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',y_harden)[0])
        #外盘
        o_dish = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[5]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',o_dish)[0])
        #振幅
        amplitude = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[6]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',amplitude)[0])
        #量比
        than = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[7]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',than)[0])
        #总市值
        all_value = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[8]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',all_value)[0])
        #市净率
        y_radio = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[9]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',y_radio)[0])
        #每股净值产
        assets = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[10]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',assets)[0])
        #流通股本
        capital = ET.xpath('/html/body/div/div[2]/div/div[2]/div[2]/dl[11]/dd/text()')[0]
        current_list.append(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5\.]+',capital)[0])
    except:
        print("url:%s无效,继续下一个url请求" % r.url)
        exit()
    dic_socket[name]=current_list
    print('当前页面数据已经存入字典...')
#插入数据
def inset_sql(small_dict):
    #清空表里原来的数据
    sql='delete from GUPIAO'
    cur.execute(sql)
    con.commit()
    sql='insert into GUPIAO(id,tody_open,volume,higest,harden,i_dish,turnover,appoint_than,current_market,radio,per_get\
,total_equity,this_charge,Turnover_rate,lowest,y_harden,o_dish,amplitude,than,all_value,y_radio,assets,capital)VALUES(\
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    print('正在向数据库写入数据....')
    for key in small_dict:
        datas=(key,small_dict[key][0],small_dict[key][1],small_dict[key][2],small_dict[key][3],small_dict[key][4],small_dict[key][5], \
               small_dict[key][6],small_dict[key][7],small_dict[key][8],small_dict[key][9],small_dict[key][10],small_dict[key][11], \
               small_dict[key][12],small_dict[key][13],small_dict[key][14],small_dict[key][15],small_dict[key][16], \
               small_dict[key][17],small_dict[key][18],small_dict[key][19],small_dict[key][20],small_dict[key][21])
        cur.execute(sql,datas)
        con.commit()
    print('数据写入完毕....')




if __name__=="__main__":
    #连接数据库
    try:
        con=pymysql.connect(host='127.0.0.1',port=3306,user='root',password='915603',db='py',charset='utf8')
    except:
        print("连接数据库成功！")
    cur=con.cursor()
    #获取u数据库字段字典
    dic_url=from_data()
    #获取url队列
    queues = creat_url(dic_url)
    #运行逻辑
    def work(times):
        """
          主要用来写工作逻辑, 只要队列不空持续处理
          队列为空时, 检查队列, 由于Queue中已经包含了wait,
          notify和锁, 所以不需要在取任务或者放任务的时候加锁解锁
          """
        i=1
        while not queues.empty():
            print("线程%s循环了%s次"%(times,i))
            i+=1
            my_url=queues.get()
            #这里的try异常处理很有必要 如果正在执行的url出错 parser_html(my_url)会返回错误
            #用异常处理可以使得while能一直工作下去 否则while循环会因为异常而退出
            try:
                parser_html(my_url)
                # 完成一个请求后向队列发送该请求已经执行完毕的信号
                queues.task_done()
            except:
                #如果传入的url无法解析输出如下   继续下一个
                print('while在继续...')
        print('队列为空，退出线程%s..'%times)



    # 多线程函数写法
    class Newthread(threading.Thread):
        def __init__(self, name, fun):
            super(Newthread, self).__init__()
            self.name = name
            self.fun = fun
        #run函数是线程启动时候运行的函数
        def run(self):
            print("线程%s正在运行"%self.name)
            self.fun(self.name)


    #创建线程池
    threads=[]
    #字典定义为全局变量这样 可以把所有的数据都存入该自带你里
    global dic_socket
    dic_socket={}
    #线程数量可以自选
    thread_all=int(input("开启的线程数目："))
    start=time.time()
    for times in range(0,thread_all):
        thread=Newthread(times,work)
        #实例化线程后开始启动线程
        thread.start()
        threads.append(thread)
    for everythread in threads:
        everythread.join()
    #等待所有的队列里的url都取完再执行下面的操作
    print("所有url都已经执行完毕...")
    print('网页请求和解析总共花费了%sS'%(time.time()-start))
    #字典数据插入数据库 其实可以parser_html函数里就插入 懒得写
    save_time=time.time()
    inset_sql(dic_socket)
    print("存取数据入库总共花费了%sS"%(time.time()-save_time))
    print('程序总共花费了%sS'%(time.time()-start))