# coding=utf-8
import datetime

import pymysql
import requests
from lxml import etree

con = pymysql.Connect(host="127.0.0.1",port=3306,user="root",password="1003",db="one",charset="utf8")
cursor = con.cursor()
sql = "select url,username,pwd,type,isget,id from website"
cursor.execute(sql)
result = cursor.fetchall()

# print(result)
s = requests.Session()
for r in result:
    if r[4]:
        continue

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

        #------------------------wordpress执行部分
    if r[3] == "wordpress":
        # s.get(url)
        n_n = url.split("-")
        n_n.pop()
        new_u = "".join(n_n)
        # print(new_u)
        n_url = "{}-login.php".format(new_u)

        erro_ = ""
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
            cursor.execute(sql,(i[-2],i[0:2],r[5]))
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
                    cursor.execute(sql,(n_d[-2],n_d[0:2],r[5]))
                    con.commit()
        sql = "update website set isget=1 where id=%s"
        cursor.execute(sql, r[5])
        con.commit()

print("全部执行完毕")


# sql = "select id from dede_inner where name=%s"
# in_new=input("想添加的类型如 新闻，军事，政治，体育")
# cursor.execute(sql,in_new)
# result_id = cursor.fetchall()
# print(result_id[0][0])
# add_url = "{}article_add.php?channelid=1&cid={}".format(url,result_id[0][0])
# last = s.get(add_url)
# print(last.text)


# sql = "select title,result from test where id=1"
# cursor.execute(sql)
# art_result = cursor.fetchall()
# print(art_result)
# art_data = {
#     "title":art_result[0][0]
#     ""
# }