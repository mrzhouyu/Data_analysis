#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/23 15:09
# @Author  : Yu
# @Site    : 
# @File    : 大学排名分析.py
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
from numpy.random import *
import numpy as np

try:
    con=pymysql.connect(host='127.0.0.1',port=3306,user='root',password='915603',db='py',charset='utf8')
    cur = con.cursor()
    print("链接数据库成功！")
except:
    print("链接数据库出错！")

sql='select rank,grade from university limit 200'
#从数据库读取数据
rows=pd.read_sql(sql,con)
#转变DaTaFrame对象
data=pd.DataFrame(rows)
data.sort_index(axis=1)
#读取开头十行 不加值的话 读取所有的数
# print(data.head(10))
#读取所有的值 数组类型<class 'numpy.ndarray'> ps:这样就可以根据numpy操作
# lis=data.values
# print(type(lis))
#数组维度 <class 'tuple'>
# print(data.shape)
# print(type(data.shape))
#类型<class 'tuple'> RangeIndex(start=0, stop=10, step=1)
# print(type(data.shape))
# print(data.index)
# print(data.mad())
# print(data.var)
# print(data.mode())
value=data.values
#分别获取矩阵的两列
x=value[:,0]
y=value[:,1]
#拿出来后只有一维数组 从小到大 按行排列axis=0  =1是按照列排序
x=np.sort(x,axis=0)
y=np.sort(y,axis=0)
# print(x,y)
plt.figure()
plt.plot(x,y,color='red',linewidth=1,linestyle='-')
plt.show()
#Data_analysis