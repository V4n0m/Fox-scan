#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import json
import time
import sys
import requests
import base64
import threading
import ipdb

from func import XMLDOM,Tools
from models import MySQLHander

HEADER={'Content-Type': 'application/json'}

#定义MYSQL句併
mysql = MySQLHander()

#threading锁
lock = threading.Lock()

#taskid的队列
taskid_thread_Dict=[]

class SqlMapAction(object):
    def __init__(self):
        xml = XMLDOM()
        self.db = MySQLHander()
        self.address = xml.GetElementByName('sqlmap').strip()

    def _get_server(self, taskid):
        sql = "select server from task where taskid = \"{0}\"".format(taskid)
        self.db.query(sql)
        server = self.db.fetchOneRow()[0]
        if server == None:
            print "[!] get server error Id:{0}".format(taskid)
            return False
        return server

    def NewTaskId(self, **kwargs):
        url = "{0}/task/new".format(self.address)
        response = json.loads(requests.get(url).text)
        if response['success']:
            db = MySQLHander()
            taskid = response['taskid']
            sql = "insert into task(`user`, `target`, `taskid`, `server`) VALUES (\"{0}\", \"{1}\", \"{2}\", \"{3}\")"\
            .format(kwargs['user'], kwargs['target'], taskid, self.address)
            if db.insert(sql) == 0L:
                print "Apply New TaskId Success!"
            else:
                print "Apply New Task Fail"
            del db
            return taskid
        else:
            return False

    def Set_Options(self, **kwargs):
        server = self._get_server(kwargs['taskid'])
        if server == False:
            return False
        url = "{0}/option/{1}/set".format(server, kwargs['taskid'])
        if "options" in kwargs:
            data = json.dumps(kwargs['options'])
        else:
            data = json.dumps({})
        response = json.loads(requests.post(url, data=data, headers=HEADER).text)
        if response['success']:
            message = "{0} Set Options successfully".format(time.strftime("[*%H:%M:%S]"))
            print(message)
            return True
        else:
            return False

    def start_scan(self, taskid, target):
        server = self._get_server(taskid)
        url = "{0}/scan/{1}/start".format(server, taskid)
        data = json.dumps({"url":target})
        response = json.loads(requests.post(url,data=data, headers=HEADER).text)
        if response['success'] == True:
            print "[!] start task {0} sucess".format(taskid)
            t = threading.Thread(target=Thread_Handle,args=(taskid,target,))
            taskid_thread_Dict.append(taskid)
            t.start()
            return True
        else:
            return False

class Action:

    @staticmethod
    def SaveData(target, data):
        sql = ""
        if len(data) == 0:
            sql = "update task set success=0 where target={1}".format(target)
        else:
            sql = "update task set data=\"{0}\",success=1 where target=\"{1}\"".format(\
                Tools.dict2base64(data['data'][0]['value'][0]['data']), target)
        return mysql.update(sql)

    @staticmethod
    def GetStatusInfo(taskid):
        '''
        :param taskid:
        :return: status,success
        '''
        sql = "select target,status,success from task where taskid=\"{0}\" ".format(taskid)
        mysql.query(sql)
        data = mysql.fetchOneRow()
        result = {"target":data[0], "status":data[1], "success":data[2]}
        return result

    @staticmethod
    def GetTaskidList():
        return taskid_thread_Dict

    @staticmethod
    def GetStatus():
        data = []
        for taskid in taskid_thread_Dict:
            result = Action.GetStatusInfo(taskid)
            data.append(result)
        return data

def Thread_Handle(taskid, target):
    lock.acquire()
    sql = SqlMapAction()
    server = sql._get_server(taskid)
    url_status = "{0}/scan/{1}/status".format(server, taskid)
    url_log = "{0}/scan/{1}/log".format(server, taskid)
    url_data="{0}/scan/{1}/data".format(server, taskid)
    response_status = json.loads(requests.get(url_status,None).text)['status']
    while response_status != "terminated" and response_status!="deleting":
        time.sleep(2)
        response_status = json.loads(requests.get(url_status,None).text)['status']
        sql = "update `task` set status = \"{0}\" where taskid=\"{1}\"".format(response_status, taskid)
        mysql.update(sql)
    response_data = json.loads(requests.get(url_data, None).text)
    if response_data==None:
        return False
    Action.SaveData(target, response_data)
    lock.release()
    return True

if __name__ == '__main__':
    Action.GetStatus("19f4cc8df5166df3")