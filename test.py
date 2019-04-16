# coding=utf-8
# import datetime
#
# import pymysql
# import requests
# from lxml import etree
#
#
#
#
#
#
# con = pymysql.Connect(host="127.0.0.1",port=3306,user="root",password="1003",db="one",charset="utf8")
# cursor = con.cursor()
# sql = "select url,username,pwd,type,isget,id from website"
# cursor.execute(sql)
# result = cursor.fetchall()
# s = requests.Session()
#
#
#
# for r in result:
#     if r[4]:
#         continue
#     if r[3] != "wordpress":
#         print("ok")
#     url = r[0]
#     username = r[1]
#     pwd = r[2]
#     sql = "select id from category where websiteid=%s"
#     cursor.execute(sql, r[5])
#     result = cursor.fetchall()
#     if result:
#         sql = "delete from category where websiteid=%s"
#         cursor.execute(sql, r[5])
#         con.commit()
#
#
#
#     s.get(url)
#     n_n=url.split("-")
#     n_n.pop()
#     new_u = "".join(n_n)
#     # print(new_u)
#     n_url="{}-login.php".format(new_u)
#
#
#     erro_ = ""
#     try:
#         res = s.get(url,timeout=10)
#         if "返回到我的网站-wordpress" not in res.text:
#             print("网址非wordpress操作系统")
#             erro_ += str(datetime.date.today()) + "  id为{},{}登陆界面不正常，非wordpress操作系统，请检查网址是否正确\n".format(r[5],url)
#             with open("erro_log.txt", "a") as f:
#                 f.write(erro_)
#             continue
#     except  Exception as e:
#         print("网址异常")
#         erro_ += str(datetime.date.today()) + "  id为{},{}登陆界面不正常，请检查网址是否正确\n".format(r[5],url)
#         with open("erro_log.txt", "a") as f:
#             f.write(erro_)
#         continue
#     print("网址正确")
#     data={
#         "log": username,
#         "pwd": pwd
#     }
#     # print(n_url)
#     res = s.post(n_url,data=data)
#     # print(res.text)
#     if "返回到我的网站-wordpress" in res.text:
#         print("登陆异常，账号或密码错误")
#         erro_ += str(datetime.date.today()) + "  id为{},{}没有正确返回登陆成功页面，请检查账号密码是否正确\n".format(r[5],url)
#         with open("erro_log.txt", "a") as f:
#             f.write(erro_)
#         continue
#     print("登陆成功")
#
#
#
#
#     n_r=s.get("{}/edit-tags.php?taxonomy=category".format(url))
#     # print(n_r.text)
#     html = etree.HTML(n_r.text)
#     tag_list=html.xpath("//a[@class='row-title']//text()")
#     tag_id_list = html.xpath("//tbody[@id='the-list']/tr/@id")
#     # print(tag_id_list)
#     print(tag_list)
#     if not tag_list:
#         print("分类目录为空，请先添加分类目录")
#         erro_ += str(datetime.date.today()) + "  id为{},{}分类目录为空\n".format(r[5], url)
#         with open("erro_log.txt", "a") as f:
#             f.write(erro_)
#         continue
#     for i in range(len(tag_list)):
#         tag = tag_list[i]
#         if tag.startswith("—"):
#             tag = tag[2:]
#         sql="insert into category(database_id,name,websiteid) values (%s,%s,%s)"
#         cursor.execute(sql,(tag_id_list[i][-1],tag,r[5]))
#         con.commit()
#     sql = "update website set isget=1 where id=%s"
#     cursor.execute(sql,r[5])
#     con.commit()
# print("全部执行完毕")
import pymysql

con = pymysql.Connect(host="127.0.0.1",port=3306,user="root",password="1003",db="one",charset="utf8")
cursor = con.cursor()
sql = "delete from keywordtask where websiteid=1"
cursor.execute(sql)
con.commit()









