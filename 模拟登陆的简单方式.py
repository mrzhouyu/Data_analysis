#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/28 21:12
# @Author  : Yu
# @Site    : 
# @File    : 模拟登陆的简单方式.py
from selenium import webdriver
import requests
import time
import json
#模拟登陆
def webdrive_start():
    driver=webdriver.Chrome()
    driver.get('https://www.zhihu.com/')
    driver.find_element_by_link_text(u"登录").click()
    driver.find_element_by_css_selector("span.signin-switch-password").click()
    driver.find_element_by_name("account").clear()
    driver.find_element_by_name("account").send_keys("username")
    driver.find_element_by_name("password").clear()
    driver.find_element_by_name("password").send_keys("password")
    driver.find_element_by_css_selector("button.sign-button.submit").click()
    #方便输入验证码等等
    time.sleep(15)
    #保存cookie 会话 这里返回的是一个列表形式
    cookies=driver.get_cookies()
    #保存cookie到本地
    with open('c.txt','w') as f:
        for c in cookies:
            ck = '{0}={1}'.format(c['name'], c['value'])
            print(type(ck))
            f.write(ck+'\n')

def deall_iner_url(jishu):
    #读取本地cookie 定义cookie字典 后面传入get
    dic = {}
    with open('c.txt', 'r') as f:
        #一直一行一行读取 直到跳出循环
        while True:
            x = f.readline()
            #判断是否读取完毕 读取完毕跳出while循环
            if not x:
                break
            #只分割一次 第一个等号
            name = x.split('=', 1)[0]
            #后面的第二个-1为了去除\n换行符
            value = x.split('=', 1)[-1][:-1]
            dic[name] = value

    req=requests.Session()
    #获得原始模拟登陆的cookie
    #不保存本地cookie的情况
    #直接给请求设置cookie 为会话对象设置cookie保持登陆
    # for cookie in cookies:
    #     req.cookies.set(cookie['name'],cookie['value'])
    #删除原始req里的爬虫标记
    req.headers.clear()
    #正式进入登陆后的网址爬取信息
    try:
        r=req.get('https://www.zhihu.com/people/excited-vczh/activities',cookies=dic)
        r.encoding=r.apparent_encoding
        r.raise_for_status()
        if r.status_code==200:
            print("内部请求成功")
        return r.text
    except:
        print("网页请求失败。。。")
        #重新获取cookie
        #清空txt里无用的cookie
        print("正在清空txt，准备重新获取cookie...")
        fp=open('c.txt','w')
        fp.close()
        #调用模拟登陆的函数重新获取cookie
        print('重新获取cookie中...')
        webdrive_start()
        #最多迭代一次 重新获取cookie后请求仍然无效 那么发生了其他问题
        if jishu<2:
            jishu+=1
            print('正在第{}次迭代...'.format(jishu-1))
            deall_iner_url(jishu)
        else:
            print("重新获取cookie登陆后还是出错,请检查其他原因...")
#解析函数 这里没写出需求
def parser(html):
    print('尽情在知乎里获得数据吧.....')

if __name__=="__main__":
    i=1
    html=deall_iner_url(i)
    parser(html)
