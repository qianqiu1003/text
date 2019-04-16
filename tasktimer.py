# coding=utf-8
import datetime
import random
import re
import time
from multiprocessing import Process,Lock

import pymysql
import requests


def FaBu(one_host,one_port,one_user,one_pwd,one_db):
    con = pymysql.Connect(host=one_host, port=one_port, user=one_user, password=one_pwd, db=one_db, charset="utf8")
    cursor = con.cursor()
    sql = "select id,nextruntime from tasktimer where nextruntime<=%s"
    cursor.execute(sql,datetime.datetime.now())
    time_result = cursor.fetchall()
    task_list=[]
    for t in time_result:
        sql = "select rooturl,minhour,maxhour,keywordtaskid,runintervaltime from tasktimer where id=%s"
        cursor.execute(sql,t[0])
        tasktimer_result = cursor.fetchone()

        lastruntime = t[1]
        nextruntime_one = datetime.date.today() + datetime.timedelta(days=tasktimer_result[-1])

        sql = "select minhour,maxhour from tasktimer where id=%s"
        cursor.execute(sql,t[0])
        min_max = cursor.fetchone()

        min_h = min_max[0]
        max_h = min_max[1]
        run_h = random.randint(min_h,max_h)
        run_m = random.randint(0,59)
        run_s = random.randint(0,59)
        nextruntime_tow = nextruntime_one.strftime("%Y-%m-%d") + " {}:{}:{}".format(run_h,run_m,run_s)
        nextruntime = datetime.datetime.strptime(nextruntime_tow,"%Y-%m-%d %H:%M:%S")
        print(nextruntime)
        sql = "update tasktimer set lastruntime=%s,nextruntime=%s where id=%s"
        cursor.execute(sql,(lastruntime,nextruntime,t[0]))
        con.commit()
        new_tuple = (tasktimer_result[0],tasktimer_result[3])

        task_list.append(new_tuple)
    con.close()
    return task_list



    #--------------------------
def FaSuccess(lock,new_task_list,one_host,one_port,one_user,one_pwd,one_db,tow_host,tow_port,tow_user,tow_pwd,tow_db):
    # print(time.time())
    # print(new_task_list)
    for i in new_task_list:
        # print(i)
        con = pymysql.Connect(host=one_host, port=one_port, user=one_user, password=one_pwd, db=one_db, charset="utf8")
        cursor = con.cursor()
        rooturl = i[0]
        keywordtaskid = i[1]
        sql = "select websiteid,categoryid,minpostcount,maxpostcount,postdone from keywordtask where id=%s"
        cursor.execute(sql,keywordtaskid)
        task_result = cursor.fetchone()
        if not task_result:
            continue
        print(task_result)
        websiteid = task_result[0]
        categoryid = task_result[1]
        min_c = task_result[2]
        max_c = task_result[3]
        #----------检测website中已删除的 如果检测到残留的清除
        sql="select id from website where rooturl=%s"
        cursor.execute(sql,rooturl)
        if not cursor.fetchone():
            sql = "delete from tasktimer where rooturl=%s"
            cursor.execute(sql,rooturl)
            con.commit()
            sql = "delete from keywordtask where websiteid=%s"
            cursor.execute(sql,websiteid)
            con.commit()
            sql = "delete from category where websiteid=%s"
            cursor.execute(sql,websiteid)
            con.commit()
            continue
        #--------------------------------------------------
        #------如果categoryid为0 需要进行另一种情况
        if categoryid ==0:
            sql = "select database_id,tobekeyword from category where tobekeyword is null and websiteid=%s"
            cursor.execute(sql,websiteid)
            new_cate_list = cursor.fetchall()
            if not new_cate_list:
                sql = "update tasktimer set success_done=1 where rooturl=%s and keywordtaskid=%s"
                cursor.execute(sql, (rooturl, keywordtaskid))
                con.commit()
                sql = "update tasktimer set resetkeyword_done=0 where rooturl=%s and keywordtaskid=%s"
                cursor.execute(sql, (rooturl, keywordtaskid))
                con.commit()
                sql = "select refresh from website where id=%s"
                cursor.execute(sql, websiteid)
                websit_result = cursor.fetchone()
                refresh = websit_result[0]

            else:

                # print(new_cate_list)
                # print(min_c,max_c)
                # print(len(new_cate_list))
                new_rand_min = min_c//len(new_cate_list)
                new_rand_max = max_c//len(new_cate_list)
                for n_cate in new_cate_list:
                    new_database_id = n_cate[0]
                    new_c_num = random.randint(new_rand_min,new_rand_max)
                    # ------------------------
                    erro_ = ""
                    try:
                        new_con = pymysql.Connect(host=tow_host, port=tow_port, user=tow_user, password=tow_pwd, db=tow_db,charset="utf8")
                    except Exception as e:
                        print("发布失败,请检查提取文章的数据库是否可以正常连接")
                        erro_ += str(datetime.date.today()) + " 请检查提取文章的数据库是否可以正常连接\n"
                        with open("erro_log.txt", "a") as f:
                            f.write(erro_)
                        continue
                    new_cursor = new_con.cursor()
                    lock.acquire()
                    l_sql = "select id,search,title,split_content from wenke_baidu_content where isfabu=0 and postdone=1 order by id limit %s"
                    new_cursor.execute(l_sql,new_c_num)
                    art_list = new_cursor.fetchall()
                    print(art_list)
                    for art in art_list:
                        result_id = art[0]

                        l_sql = "update wenke_baidu_content set isfabu=1 where id = %s"
                        new_cursor.execute(l_sql,result_id)
                        new_con.commit()
                    lock.release()
                    for art in art_list:
                        result_title = art[2]
                        result_content = art[3]
                        last_title = result_title
                        last_content = result_content
                    #获取posturl接口
                        sql = "select posturl,uploadurl,type,refresh from website where id=%s"
                        cursor.execute(sql,websiteid)
                        websit_result = cursor.fetchone()
                        posturl = websit_result[0]
                        uploadurl = websit_result[1]
                        n_type = websit_result[2]
                        refresh = websit_result[3]
                        if n_type == "dedecms":
                            data = {
                                "arcticle_title": last_title,
                                "auth": "eddie",
                                "type_id": new_database_id,
                                "arcticle_content": last_content,
                            }
                            success_p=requests.post(posturl,data=data)
                            print(success_p.text)

                            # img_data = {
                            #     "auth": "eddie",
                            #     "path": "/images/",
                            # }
                            # img_list =re.findall('src="(.*?)"',last_content)
                            # # print(img_list)
                            # for img_path in img_list:
                            #
                            #     files = {"file": open(img_path, "rb")}
                            #     res = requests.post(url, files=files, data=img_data)
                sql = "update tasktimer set success_done=1 where rooturl=%s and keywordtaskid=%s"
                cursor.execute(sql,(rooturl,keywordtaskid))
                con.commit()
                sql = "update tasktimer set resetkeyword_done=0 where rooturl=%s and keywordtaskid=%s"
                cursor.execute(sql, (rooturl, keywordtaskid))
                con.commit()
                # print("------------------------0")
                        # elif n_type == "wordpress":
                        #     #-----------------待开发
                        #     pass

                    #------------------------

        #------
        else:
            sql = "select database_id,tobekeyword from category where id=%s"
            cursor.execute(sql,categoryid)
            cate_result = cursor.fetchone()
            # print(cate_result)
            database_id = cate_result[0]
            tobekeyword = cate_result[1]
            c_num = random.randint(min_c,max_c)
            #------------
            #
            #------------
            erro_=""
            try:
                new_con = pymysql.Connect(host=tow_host, port=tow_port, user=tow_user, password=tow_pwd, db=tow_db, charset="utf8")
            except Exception as e:
                print("请检查提取文章的数据库是否可以正常连接")
                erro_ += str(datetime.date.today()) + " 请检查提取文章的数据库是否可以正常连接\n"
                with open("erro_log.txt", "a") as f:
                    f.write(erro_)
                continue
            new_cursor = new_con.cursor()
            lock.acquire()
            l_sql = "select id,search,title,split_content from wenke_baidu_content where isfabu=0 and postdone=1 order by id limit %s"
            new_cursor.execute(l_sql,c_num)
            art_list = new_cursor.fetchall()
            print(art_list)
            for art in art_list:
                result_id = art[0]

                l_sql = "update wenke_baidu_content set isfabu=1 where id = %s"
                new_cursor.execute(l_sql,result_id)
                new_con.commit()
            lock.release()
            for art in art_list:
                result_keyword = art[1]
                result_title = art[2]
                result_content = art[3]
                if result_title:
                    last_title = result_title.replace(result_keyword, tobekeyword)
                else:
                    last_title = result_title
                last_content = result_content.replace(result_keyword, tobekeyword)
            #获取posturl接口
                sql = "select posturl,uploadurl,url,username,pwd,type,refresh from website where id=%s"
                cursor.execute(sql,websiteid)
                websit_result = cursor.fetchone()
                posturl = websit_result[0]
                uploadurl = websit_result[1]
                url = websit_result[2]
                username = websit_result[3]
                pwd = websit_result[4]
                n_type = websit_result[5]
                refresh = websit_result[6]
                if n_type == "dedecms":
                    data = {
                        "arcticle_title":last_title,
                        "auth": "eddie",
                        "type_id": database_id,
                        "arcticle_content": last_content,
                    }
                    success_p=requests.post(posturl,data=data)
                    print(success_p.text)
                    # img_data = {
                    #     "auth": "eddie",
                    #     "path": "/images/",
                    # }
                    # img_list =re.findall('src="(.*?)"',last_content)
                    # # print(img_list)
                    # for img_path in img_list:
                    #
                    #     files = {"file": open(img_path, "rb")}
                    #     res = requests.post(url, files=files, data=img_data)
            sql = "update tasktimer set success_done=1 where rooturl=%s and keywordtaskid=%s"
            cursor.execute(sql, (rooturl, keywordtaskid))
            con.commit()
            sql = "update tasktimer set resetkeyword_done=0 where rooturl=%s and keywordtaskid=%s"
            cursor.execute(sql, (rooturl,keywordtaskid))
            con.commit()
                # elif n_type == "wordpress":
                    #-----------------待开发
                    # pass
        #重置tobekeyword
        sql = "select success_done from tasktimer where rooturl=%s"
        cursor.execute(sql, rooturl)
        success_d = cursor.fetchall()
        s_one_y = False
        for i in success_d:
            if not i[0]:
                s_one_y = True
                break
        if s_one_y:
            continue
        sql = "select resetkeyword_done from tasktimer where rooturl=%s"
        cursor.execute(sql, rooturl)
        reset_d = cursor.fetchall()
        r_one_y = False
        for i in reset_d:
            if i[0]:
                r_one_y = True
                break
        if r_one_y:
            continue
        sql = "select lastruntime from tasktimer where rooturl=%s and resetkeyword_done=0"
        cursor.execute(sql,rooturl)
        reset_r = cursor.fetchall()
        r_y=True
        all_y=False
        for i in reset_r:
            if not i[0]:
                all_y=True
                break
            if i[0] >datetime.datetime.now():
                r_y=False
                break
        if all_y:
            continue
        if reset_r and r_y:
            #----
            try:
                if refresh:
                    requests.get(refresh)
                    print("--------------------------refresh success!------------------------")
            except Exception as e:
                print(e)
            fin_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "update website set time=%s where rooturl=%s"
            cursor.execute(sql, (fin_time, rooturl))
            con.commit()
            #----
            sql= "update tasktimer set resetkeyword_done=1 where rooturl=%s"
            cursor.execute(sql,rooturl)
            con.commit()
            sql = "update tasktimer set success_done=0 where rooturl=%s"
            cursor.execute(sql, rooturl)
            con.commit()
            sql = "select name,id from website where rooturl=%s"
            cursor.execute(sql, rooturl)
            reweb_result = cursor.fetchone()
            print(reweb_result)
            w_name = reweb_result[0]
            sql = "select bz_keywords from resetkeyword where name=%s"
            cursor.execute(sql, w_name)
            reset_result = cursor.fetchall()
            # print(reset_result)
            # new_r_list = reset_result[0][0].split(",")
            new_r_list = re.split(",|，",reset_result[0][0])
            print(new_r_list)
            # reset_list = (s for s in new_r_list)
            sql = "select tobekeyword,id from category where websiteid=%s and tobekeyword is not null "
            cursor.execute(sql, websiteid)
            to_result = cursor.fetchall()
            print(to_result)
            ins_k_list=[]
            for in_tk in to_result:
                sql = "update category set tobekeyword=%s where id=%s"
                ins_k = random.choice(new_r_list)
                if ins_k_list:
                    ins_num = 1
                    while ins_num:
                        ins_num+=1
                        if ins_num >20:
                            break
                        if ins_k not in ins_k_list:
                            ins_num=0
                            break
                        ins_k = random.choice(new_r_list)
                cursor.execute(sql,(ins_k,in_tk[1]))
                con.commit()
                ins_k_list.append(ins_k)

if __name__ == '__main__':
    tas_list = []
    with open("tasktimer.txt", "r", encoding='utf8') as f:
        task_l = f.readlines()
    for i in task_l:
        new_f = i.split(":")
        if len(new_f)==2:
            tas_list.append(new_f[1].strip())
    # print(tas_list)
    one_host = tas_list[0]
    one_port = int(tas_list[1])
    one_user = tas_list[2]
    one_pwd = tas_list[3]
    one_db = tas_list[4]
    tow_host = tas_list[5]
    tow_port = int(tas_list[6])
    tow_user = tas_list[7]
    tow_pwd = tas_list[8]
    tow_db = tas_list[9]

    while True:
        t_list=FaBu(one_host,one_port,one_user,one_pwd,one_db)
        # print(t_list)
        if t_list:
            new_t_list=[]
            for i in range(len(t_list)):
                new_t_list.append(t_list[i:i+1])
            # print(new_t_list)
            lock = Lock()
            l=[]
            for n in new_t_list:
                p=Process(target=FaSuccess,args=(lock,n,one_host,one_port,one_user,one_pwd,one_db,tow_host,tow_port,tow_user,tow_pwd,tow_db))
                l.append(p)
                p.start()
            for i in l:
                i.join()



