# coding=utf-8
import datetime
import random

import pymysql

con = pymysql.Connect(host="127.0.0.1", port=3306, user="root", password="1003", db="one", charset="utf8")
cursor = con.cursor()
min_y_c = 2
max_y_c = 5
min_n_c = 10
max_n_c = 20
sql ="select id,websiteid from category where tobekeyword is not null "
cursor.execute(sql)
begin_task_list = cursor.fetchall()
# print(begin_task_list)
if begin_task_list:
    for i in begin_task_list:
        task_category_id = i[0]
        task_websiteid = i[1]
        sql = "insert into keywordtask(websiteid,categoryid,insertdatetime,minpostcount,maxpostcount) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql,(task_websiteid,task_category_id,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),min_y_c,max_y_c))
        con.commit()
    sql = "insert into keywordtask(websiteid,categoryid,insertdatetime,minpostcount,maxpostcount) VALUES (%s,0,%s,%s,%s)"
    cursor.execute(sql, (task_websiteid, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),min_n_c,max_n_c))
    con.commit()
#

#-----------------------------------add tasktimer-------------------------------#
# con = pymysql.Connect(host="127.0.0.1", port=3306, user="root", password="1003", db="one", charset="utf8")
# cursor = con.cursor()
sql = "select id,websiteid from keywordtask where postdone=0"
cursor.execute(sql)
timer_list = cursor.fetchall()
minhour = 8
maxhour = 22
b_runintervaltime = 1
print(timer_list)
for t in timer_list:
    timer_websiteid = t[1]
    timer_task_id = t[0]
    sql = "select rooturl from website where id=%s"
    cursor.execute(sql,timer_websiteid)
    root_url = cursor.fetchone()
    # print(root_url)
    rooturl = root_url[0]

    last_h = random.randint(minhour,maxhour)
    last_m = random.randint(0,59)
    last_s = random.randint(0,59)
    # run_h = random.randint(minhour, maxhour)
    # run_m = random.randint(0, 59)
    # run_s = random.randint(0, 59)
    lastruntime = datetime.datetime.now().strftime("%Y-%m-%d") + " {}:{}:{}".format(last_h,last_m,last_s)
    # b_nextruntime_one = datetime.date.today() + datetime.timedelta(days=b_runintervaltime)
    # b_nextruntime_tow = b_nextruntime_one.strftime("%Y-%m-%d") + " {}:{}:{}".format(run_h, run_m, run_s)
    sql = "insert into tasktimer(rooturl,minhour,maxhour,nextruntime,keywordtaskid,runintervaltime) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql,(rooturl,minhour,maxhour,lastruntime,timer_task_id,b_runintervaltime))
    con.commit()

