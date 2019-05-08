﻿# -*- coding:utf-8 -*-

import socket as Socket
import threading
import json 
import mysql.connector
#用来判断动作的switcher
ACTION_LOGIN = 100
ACTION_GET_CAR = 100
ACTION_CAR_SAVE = 123
#用来检查账号查询结果的switcher
RESULT_ERROR = 11
RESULT_REGISTER = 12
RESULT_SUCCESS = 10
#存放用户的id，在注册用户或者密码正确时赋值
global ID
def Main():
    soc = Socket.socket(Socket.AF_INET,Socket.SOCK_STREAM)
    soc.bind(('0.0.0.0',8080))
    soc.listen(20)
    while True:
        s , addr = soc.accept()
        print('connect %s:%s ' % (addr))
        # print(s.recv(1024).decode('utf-8'))
        t = threading.Thread(target=handleMessage,args=(s,addr))
        print('开启了一个新的线程')
        t.start()

#json解析
# jsonStr = '{"account":"123213","password":"213"}'
# parJson = json.loads(jsonStr)
# print(parJson['account'])
# print(parJson)

def handleMessage(soc,addr):
    print('start handle message')
    while True:
        recStr = soc.recv(1024).decode('utf-8')
        jsonParser = json.loads(recStr)
        #用字典模拟的switch
        if jsonParser['action'] == ACTION_LOGIN:        #action是login的话需要输入参数，进行特殊处理
            result = messageSwitcher[jsonParser['action']](jsonParser['account'],jsonParser['password'])    #模拟switch来处理事务
        else:                                           #不需要参数，直接运行函数
            result = messageSwitcher[jsonParser['action']]()
        # result = messSwitcher[jsonParser['action']](jsonParser['account'],jsonParser['password'])     #两个方括号get到字典和json字符串的值，最后一个小括号传入参数和运行函数
    	sendStr = '%d'%(result)
        soc.send(sendStr)
        print('返回结果 %d' % result)

#一下几个函数是处理对应的Action的
def loginCheck(account,password):
    sqlConnect = mysql.connector.connect(user='root',password='Yt00206.',database='garage')
    cursor = sqlConnect.cursor()    #处理sql事务的客户端
    #查询账号
    cursor.execute('SELECT * FROM accounts WHERE account="%s"' % account)
    #提交事务
    #sqlConnect.commit()   #报错
    #获得结果
    result = cursor.fetchall()
    print(result)
    if result == []:    #如果列表为空，说明这个还没被注册过
        registerNewAccount(sqlConnect,cursor,account,password)
        print('注册成功')
        ID = account
        return RESULT_REGISTER
    else:               #列表不是空，表示已有该账户
        if password == result[0][2]: #[0]表示唯一的一个数据，[2]表示密码栏目在返回的tuple里面的第三个位置，例如[(1, u'admin', u'123456')]
            ID = account
            return RESULT_SUCCESS
        else :
            return RESULT_ERROR

def carGet():
    return 1

def carSave():
    return 1

def registerNewAccount(sqlConnect,sqlCursor,account,password):
    sqlCursor.execute('INSERT INTO accounts (account,password) values ("%s","%s")' % (account,password) )
    sqlConnect.commit()


messageSwitcher = {
    ACTION_LOGIN : loginCheck,
    ACTION_CAR_SAVE : carSave,
    ACTION_GET_CAR : carGet
}
if __name__ == '__main__':
    Main()
