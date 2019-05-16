# -*- coding:utf-8 -*-

import socket as Socket
import threading
import json 
import mysql.connector
import logging as Log
#用来判断动作的switcher
ACTION_LOGIN = -100
ACTION_GET_CAR = 100
ACTION_CAR_SAVE = 123
#用来检查账号查询结果的switcher
RESULT_ERROR = 11
RESULT_REGISTER = 12
RESULT_SUCCESS = 10
#Save the mapping between Garage Number and each Gararge's soc
garageSoc = None
#存放用户的id，在注册用户或者密码正确时赋值
global ID
def Main():
    #这一行代码是开启车库Socket线程获取的
    #threading.Thread(target=getGarageSocket()).start()
    #
    #print('开启了车库Socket接收线程，同时开始监听APP')
    Log.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=Log.DEBUG,filemode='a',filename="server.log")
    soc = Socket.socket(Socket.AF_INET,Socket.SOCK_STREAM)
    accThread = threading.Thread(target=thread_acceptSocket,args=(soc,)) 
    accThread.start()
    Log.info('开始了一个accept线程')
    #以下的被暂时注释掉
    #soc.bind(('0.0.0.0',8080))
    #soc.listen(20)
    #while True:
#        s , addr = soc.accept()
 #       print('connect %s:%s ' % (addr))
  #      #.settimeout(10)    #10秒的timeout，当recv阻塞10秒时就会自动断开链接。安卓端发送心跳包7S一次
   #     #如果设置timeout的话车库端无法给我发送心跳包
    #    s.send('111'.encode())
     #   # print(s.recv(1024).decode('utf-8'))
      #  s.send('ojbk'.encode())
       # #.settimeout(5) 不能直接设置timeout，因为如果recv5S没有接收到数据的话就会直接关闭，和嵌入式方面链接会有bug
        ##  print(s.recv(1024).decode('utf-8'))
        #t = threading.Thread(target=handleMessage,args=(s,addr))
        #print('创建了一个新的线程')
        #t.start()
        #print('新线程开始')

#json解析
# jsonStr = '{"account":"123213","password":"213"}'
# parJson = json.loads(jsonStr)
# print(parJson['account'])
# print(parJson)

def thread_acceptSocket(soc):
    soc.bind(('0.0.0.0',8080))
    soc.listen(20)
    while True:
        Log.info('开始了新一轮的Accept')
        s , addr = soc.accept()
        Log.info('connect %s:%s ' % (addr))
        #.settimeout(10)    #10秒的timeout，当recv阻塞10秒时就会自动断开链接。安卓端发送心跳包7S一次
        #如果设置timeout的话车库端无法给我发送心跳包
        #s.send('111'.encode())
        # print(s.recv(1024).decode('utf-8'))
        s.send('ojbk'.encode())
        #.settimeout(5) 不能直接设置timeout，因为如果recv5S没有接收到数据的话就会直接关闭，和嵌入式方面链接会有bug
        #  print(s.recv(1024).decode('utf-8'))
        t = threading.Thread(target=handleMessage,args=(s,addr))
        Log.info('创建了一个新的线程')
        t.start()
        Log.info('新线程开始')

def handleMessage(soc,addr):
    while True:
        try:
            Log.info('开始一轮处理信息')
            buf = soc.recv(1024)
            Log.info('收到数据',buf.decode())
            if len(buf) == 0:
                Log.warning('链接断开')
                break
            recStr = buf.decode('utf-8')
            jsonParser = json.loads(recStr)
        except Exception as e:
            Log.error('error:',e)
            continue
        #用字典模拟的switch
        if jsonParser['action'] == ACTION_LOGIN:        #action是login的话需要输入参数，进行特殊处理
            result = messageSwitcher[jsonParser['action']](jsonParser['account'],jsonParser['password'])    #模拟switch来处理事务
        else:                                           #不需要参数，直接运行函数
            result = messageSwitcher[jsonParser['action']]()
        # result = messSwitcher[jsonParser['action']](jsonParser['account'],jsonParser['password'])     #两个方括号get到字典和json字符串的值，最后一个小括号传入参数和运行函数
        sendStr = '%d' % (result)
        soc.send(sendStr)
        Log.info('返回结果 %s' % sendStr)

#一下几个函数是处理对应的Action的
def loginCheck(account,password):
    Log.info('进入账户检查函数')
    sqlConnect = mysql.connector.connect(user='root',password='Yt00206.',database='garage')
    cursor = sqlConnect.cursor()    #处理sql事务的客户端
    #查询账号
    cursor.execute('SELECT * FROM accounts WHERE account="%s"' % account)
    #提交事务
    #sqlConnect.commit()   #报错
    #获得结果
    result = cursor.fetchall()
    Log.info(result)
    if result == []:    #如果列表为空，说明这个还没被注册过
        registerNewAccount(sqlConnect,cursor,account,password)
        Log.info('注册成功')
        ID = account
        return RESULT_REGISTER
    else:               #列表不是空，表示已有该账户
        if password == result[0][2]: #[0]表示唯一的一个数据，[2]表示密码栏目在返回的tuple里面的第三个位置，例如[(1, u'admin', u'123456')]
            Log.info('密码正确')
            ID = account
            return RESULT_SUCCESS
        else :
            return RESULT_ERROR

def carGet():
    Log.info('有用户取车')
    return 1

def carSave():
    Log.info('有用户存车')
    return 1

def registerNewAccount(sqlConnect,sqlCursor,account,password):
    sqlCursor.execute('INSERT INTO accounts (account,password) values ("%s","%s")' % (account,password) )
    sqlConnect.commit()

def getGarageSocket():
    global garageSoc
    garageSer = Socket.socket(Socket.AF_INET,Socket.SOCK_STREAM)
    garageSer.bind(('',8081))
    garageSer.listen(10)
    [garageSoc , addr] = garageSer.accept()
    Log.info('来了一个车库Socket')

socMapping = {
    1 : garageSoc
}
messageSwitcher = {
    ACTION_LOGIN : loginCheck,
    ACTION_CAR_SAVE : carSave,
    ACTION_GET_CAR : carGet
}
if __name__ == '__main__':
    Main()
