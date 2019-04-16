# coding=utf-8

import datetime
import random
import re

import pymysql
import requests
from lxml import etree
def Initialize(host,port,user,password,db,len_max,len_min,c_y_min,c_y_max,c_n_min,c_n_max,time_min,time_max,time_runinterval):
    #--------------1.登陆账号获取目录
    con = pymysql.Connect(host=host,port=port,user=user,password=password,db=db,charset="utf8")
    cursor = con.cursor()
    sql = "select url,username,pwd,type,isget,id,rooturl from website where isget=0"
    cursor.execute(sql)
    result = cursor.fetchall()

    # print(result)
    s = requests.Session()
    for r in result:

        url = r[0]
        username = r[1]
        pwd = r[2]
        sql = "select id from category where websiteid=%s"
        cursor.execute(sql,r[5])
        result = cursor.fetchall()
        if result:
            sql ="delete from category where websiteid=%s"
            cursor.execute(sql,r[5])
            con.commit()
            sql = "delete from keywordtask where websiteid=%s"
            cursor.execute(sql,r[5])
            con.commit()
            sql =  "delete from tasktimer where rooturl=%s"
            cursor.execute(sql,r[6])
            con.commit()

            #------------------------wordpress执行部分
        if r[3] == "wordpress":
            erro_ = ""
            try:
                s.get(url)
            except Exception as e:
                print("网址异常")
                erro_ += str(datetime.date.today()) + "  id为{},{}登陆界面不正常，请检查网址是否正确\n".format(r[5], url)
                with open("erro_log.txt", "a") as f:
                    f.write(erro_)
                continue
            n_n = url.split("-")
            n_n.pop()
            new_u = "".join(n_n)
            # print(new_u)
            n_url = "{}-login.php".format(new_u)


            try:
                res = s.get(url, timeout=10)
                if "返回到我的网站-wordpress" not in res.text:
                    print("网址非wordpress操作系统")
                    erro_ += str(datetime.date.today()) + "  id为{},{}登陆界面不正常，非wordpress操作系统，请检查网址是否正确\n".format(r[5], url)
                    with open("erro_log.txt", "a") as f:
                        f.write(erro_)
                    continue
            except  Exception as e:
                print("网址异常")
                erro_ += str(datetime.date.today()) + "  id为{},{}登陆界面不正常，请检查网址是否正确\n".format(r[5], url)
                with open("erro_log.txt", "a") as f:
                    f.write(erro_)
                continue
            print("网址正确")
            data = {
                "log": username,
                "pwd": pwd
            }
            # print(n_url)
            res = s.post(n_url, data=data)
            # print(res.text)
            if "返回到我的网站-wordpress" in res.text:
                print("登陆异常，账号或密码错误")
                erro_ += str(datetime.date.today()) + "  id为{},{}没有正确返回登陆成功页面，请检查账号密码是否正确\n".format(r[5], url)
                with open("erro_log.txt", "a") as f:
                    f.write(erro_)
                continue
            print("登陆成功")

            n_r = s.get("{}/edit-tags.php?taxonomy=category".format(url))
            # print(n_r.text)
            html = etree.HTML(n_r.text)
            tag_list = html.xpath("//a[@class='row-title']//text()")
            tag_id_list = html.xpath("//tbody[@id='the-list']/tr/@id")
            # print(tag_id_list)
            print(tag_list)
            if not tag_list:
                print("分类目录为空，请先添加分类目录")
                erro_ += str(datetime.date.today()) + "  id为{},{}分类目录为空\n".format(r[5], url)
                with open("erro_log.txt", "a") as f:
                    f.write(erro_)
                continue
            for i in range(len(tag_list)):
                tag = tag_list[i]
                if tag.startswith("—"):
                    tag = tag[2:]
                sql = "insert into category(database_id,name,websiteid) values (%s,%s,%s)"
                cursor.execute(sql, (tag_id_list[i][-1], tag, r[5]))
                con.commit()
            sql = "update website set isget=1 where id=%s"
            cursor.execute(sql, r[5])
            con.commit()
        else:


            erro_=""
            try:
                res = s.get("{}login.php".format(url),timeout=10)
                if "织梦内容管理系统 V57_UTF8_SP2" not in res.text:
                    print("网址非织梦操作系统")
                    erro_ += str(datetime.date.today())+"  id为{},{}登陆界面不正常，非织梦操作系统，请检查网址是否正确\n".format(r[5],url)
                    with open("erro_log.txt", "a") as f:
                        f.write(erro_)
                    continue
            except  Exception as e:
                print("网址异常")
                erro_ += str(datetime.date.today())+"  id为{},{}登陆界面不正常，请检查网址是否正确\n".format(r[5],url)
                with open("erro_log.txt", "a") as f:
                    f.write(erro_)
                continue

            print("网址正确")
            data = {
                        "userid": username,
                        "pwd": pwd,
                        "gotopage":"/dede/",
                        "dopost": "login",
                        "adminstyle":"newdedecms",
                    }
            a_a=s.post("{}login.php".format(url),data=data)
            if "成功登录，正在转向管理管理主页！" not in a_a.text:
                print("登陆异常")
                erro_ += str(datetime.date.today())+"  id为{},{}没有正确返回登陆成功页面，请检查账号密码是否正确\n".format(r[5],url)
                with open("erro_log.txt","a") as f:
                    f.write(erro_)
                continue
            print("登陆成功")
            # bb=s.get(url)
            # print(bb.text)

            c=s.get("{}catalog_main.php".format(url))
            # print(c.text)
            html = etree.HTML(c.text)
            d=html.xpath("//td[@class='bline']//td[1]//a[1]//text()")


            if not d:
                print("网站栏目为空，请先添加网站栏目")
                erro_ += str(datetime.date.today()) + "  id为{},{}网站栏目为空\n".format(r[5], url)
                with open("erro_log.txt", "a") as f:
                    f.write(erro_)
                continue
            print(d)
            for i in d:
                sql="insert into category(database_id,name,websiteid) values (%s,%s,%s)"
                cursor.execute(sql,(i[-2],i[0:-6],r[5]))
                con.commit()

            for n in range(len(d)):
                z_res = s.get("{}catalog_do.php?dopost=GetSunLists&cid={}".format(url,n+1))
                # print(z_res.text)
                inner_h = etree.HTML(z_res.text)
                d_d = inner_h.xpath("//td[1]/a[1]//text()")
                if d_d:
                    print(d_d)
                    for n_d in d_d:
                        sql = "insert into category(database_id,name,websiteid) values (%s,%s,%s)"
                        cursor.execute(sql,(n_d[-2],n_d[0:-6],r[5]))
                        con.commit()
            # sql = "update website set isget=1 where id=%s"
            # cursor.execute(sql, r[5])
            # con.commit()

    print("全部执行完毕")
    #---------------2.初始化为目录添加对应的tobekeyword
    sql = "select name,id from website where isget=0"
    cursor.execute(sql)
    result = cursor.fetchall()
    # print(result)
    for i in result:
        sql = "update website set isget=1 where id=%s"
        cursor.execute(sql, i[1])
        con.commit()
        name = i[0]
        if not name:
            continue
        website_id = i[1]
        sql = "select bz_keywords from resetkeyword where name=%s"
        cursor.execute(sql,name)
        reset_result=cursor.fetchall()
        if reset_result:
        # print(reset_result)
        # new_r_list = reset_result[0][0].split(",")

            new_r_list = re.split(",|，", reset_result[0][0])
            random.shuffle(new_r_list)
            reset_list = (s for s in new_r_list)
            sql = "select tobekeyword,id from category where websiteid=%s and done=0"
            cursor.execute(sql,website_id)
            to_result = cursor.fetchall()
            # print(to_result)
            if not to_result:
                continue
            y_k = False
            c_id_list = []
            for k in to_result:
                if k[0]:
                    y_k = True
                    break
                c_id_list.append(k[1])
            if y_k:
                # print("ok")
                continue
            num = len(to_result)
            if num>=len_max:
                insert_list = random.sample(c_id_list,3)
                for c_id in insert_list:
                    sql = "update category set tobekeyword=%s where id=%s"
                    cursor.execute(sql,(next(reset_list),c_id))
                    con.commit()
            elif len_min<num<len_max:
                insert_list = random.sample(c_id_list, 2)
                for c_id in insert_list:
                    sql = "update category set tobekeyword=%s where id=%s"
                    cursor.execute(sql, (next(reset_list), c_id))
                    con.commit()
            elif num <=len_min:
                insert_list = random.choice(c_id_list)
                # print(c_id_list)
                # print(insert_list)
                sql = "update category set tobekeyword=%s where id=%s"
                cursor.execute(sql, (next(reset_list), insert_list))
                con.commit()
        else:
            sql = "insert into keywordtask(websiteid,categoryid,insertdatetime,minpostcount,maxpostcount) VALUES (%s,0,%s,%s,%s)"
            cursor.execute(sql,(website_id,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),c_n_min,c_n_max))
            sql = "update category set done=1 where websiteid=%s"
            cursor.execute(sql,website_id)
            con.commit()
    #-----------------------------3.初始化keywordtask表
    min_y_c = c_y_min
    max_y_c = c_y_max
    min_n_c = c_n_min
    max_n_c = c_n_max
    sql ="select id,websiteid from category where tobekeyword is not null and done=0"
    cursor.execute(sql)
    begin_task_list = cursor.fetchall()
    # print(begin_task_list)
    w_set=set()
    if begin_task_list:
        # for i in begin_task_list:
        #     del_task_category_id = i[0]
        #     del_task_websiteid = i[1]
        #     sql = "delete from keywordtask where websiteid=%s"
        #     cursor.execute(sql, del_task_websiteid)
        #     con.commit()

        for i in begin_task_list:
            task_category_id = i[0]
            task_websiteid = i[1]
            sql = "insert into keywordtask(websiteid,categoryid,insertdatetime,minpostcount,maxpostcount) VALUES (%s,%s,%s,%s,%s)"
            cursor.execute(sql,(task_websiteid,task_category_id,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),min_y_c,max_y_c))
            con.commit()
            sql = "update category set done=1 where id=%s"
            cursor.execute(sql, task_category_id)
            con.commit()
            if i[1] in w_set:
                continue
            sql = "select id from category where tobekeyword is null and websiteid=%s"
            cursor.execute(sql,i[1])
            is_n_r = cursor.fetchone()
            if not is_n_r:
                continue
            sql = "insert into keywordtask(websiteid,categoryid,insertdatetime,minpostcount,maxpostcount) VALUES (%s,0,%s,%s,%s)"
            cursor.execute(sql, (task_websiteid, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),min_n_c,max_n_c))
            con.commit()
            sql = "update category set done=1 where websiteid=%s"
            cursor.execute(sql, task_websiteid)
            con.commit()
            w_set.add(i[1])


    # sql = "select id from category where tobekeyword is null and done=0"
    # cursor.execute(sql)
    # begin_task_list = cursor.fetchall()
    # if begin_task_list:
    #     for i in begin_task_list:
    #         task_category_id = i[0]
    #         sql = "update category set done=1 where id=%s"
    #         cursor.execute(sql,task_category_id)
    #         con.commit()


    #-----------------------------4.初始化tasktimer表
    sql = "select id,websiteid from keywordtask where postdone=0"
    cursor.execute(sql)
    timer_list = cursor.fetchall()
    min_hour = time_min
    max_hour = time_max
    b_runintervaltime = time_runinterval
    # print(timer_list)
    for t in timer_list:
        timer_websiteid = t[1]
        timer_task_id = t[0]
        sql = "select rooturl from website where id=%s"
        cursor.execute(sql,timer_websiteid)
        root_url = cursor.fetchone()
        # print(root_url)
        rooturl = root_url[0]

        last_h = random.randint(min_hour,max_hour)
        last_m = random.randint(0,59)
        last_s = random.randint(0,59)
        # run_h = random.randint(minhour, maxhour)
        # run_m = random.randint(0, 59)
        # run_s = random.randint(0, 59)
        lastruntime = datetime.datetime.now().strftime("%Y-%m-%d") + " {}:{}:{}".format(last_h,last_m,last_s)
        # b_nextruntime_one = datetime.date.today() + datetime.timedelta(days=b_runintervaltime)
        # b_nextruntime_tow = b_nextruntime_one.strftime("%Y-%m-%d") + " {}:{}:{}".format(run_h, run_m, run_s)
        sql = "insert into tasktimer(rooturl,minhour,maxhour,nextruntime,keywordtaskid,runintervaltime) VALUES (%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,(rooturl,min_hour,max_hour,lastruntime,timer_task_id,b_runintervaltime))
        con.commit()
        sql = "update keywordtask set postdone=1 where id=%s"
        cursor.execute(sql,timer_task_id)
        con.commit()
if __name__ == '__main__':
    f_list=[]
    with open("fabu.txt", "r", encoding='utf8') as f:
        fabu_list = f.readlines()
    for i in fabu_list:
        new_f = i.split(":")
        if len(new_f)==2:
            f_list.append(new_f[1].strip())
    # print(f_list)
    host = f_list[0]
    port = int(f_list[1])
    user = f_list[2]
    password = f_list[3]
    db = f_list[4]
    len_max = int(f_list[5])
    len_min = int(f_list[6])
    c_y_min = int(f_list[7])
    c_y_max = int(f_list[8])
    c_n_min = int(f_list[9])
    c_n_max = int(f_list[10])
    time_min = int(f_list[11])
    time_max = int(f_list[12])
    time_runinterval = int(f_list[13])
    Initialize(host,port,user,password,db,len_max,len_min,c_y_min,c_y_max,c_n_min,c_n_max,time_min,time_max,time_runinterval)
