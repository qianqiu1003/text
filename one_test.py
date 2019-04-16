# coding=utf-8
import random
import re

import pymysql

con = pymysql.Connect(host="127.0.0.1",port=3306,user="root",password="1003",db="one",charset="utf8")
cursor = con.cursor()
sql = "select name,id from website"
cursor.execute(sql)
result = cursor.fetchall()
print(result)
for i in result:
    name = i[0]
    if not name:
        continue
    website_id = i[1]
    sql = "select bz_keywords from resetkeyword where name=%s"
    cursor.execute(sql,name)
    reset_result=cursor.fetchall()
    # print(reset_result)
    # new_r_list = reset_result[0][0].split(",")
    new_r_list = re.split(",|，", reset_result[0][0])
    random.shuffle(new_r_list)
    reset_list = (s for s in new_r_list)
    sql = "select tobekeyword,id from category where websiteid=%s"
    cursor.execute(sql,website_id)
    to_result = cursor.fetchall()
    print(to_result)
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
        print("ok")
        continue
    num = len(to_result)
    if num>=6:
        insert_list = random.sample(c_id_list,3)
        for c_id in insert_list:
            sql = "update category set tobekeyword=%s where id=%s"
            cursor.execute(sql,(next(reset_list),c_id))
            con.commit()
    elif 4<num<6:
        insert_list = random.sample(c_id_list, 2)
        for c_id in insert_list:
            sql = "update category set tobekeyword=%s where id=%s"
            cursor.execute(sql, (next(reset_list), c_id))
            con.commit()
    elif num <4:
        insert_list = random.choice(c_id_list)
        for c_id in insert_list:
            sql = "update category set tobekeyword=%s where id=%s"
            cursor.execute(sql, (next(reset_list), c_id))
            con.commit()


