

from django.shortcuts import render,HttpResponse,redirect

# Create your views here.

from rbac.models import User

def login(request):
    if request.method=="POST":
        user=request.POST.get("user")
        pwd=request.POST.get("pwd")

        user=User.objects.filter(user=user,pwd=pwd).first()
        if user:
            # 存储登录状态
            request.session["user"]=user.user
            # print(request.session["user"],234)

            # 查询当前登录用户的所有权限url
            print(user.roles.all().values("permissions__url"))
            permissions=user.roles.all().values("permissions__url","permissions__code","permissions__title").distinct()

            permission_list=[]
            permission_menu_list=[]
            for item in permissions:
                permission_list.append(item["permissions__url"])

                if item["permissions__code"]=="list":
                    permission_menu_list.append({
                        "url":item["permissions__url"],
                        "title":item["permissions__title"],
                    })
            # print(000, permission_menu_list)

            # print("permission_list",permission_list)

            # 将权限列表存储到session中
            request.session["permission_list"]=permission_list
            # 将菜单权限列表注册到session中
            # print("permission_menu_list",permission_menu_list) # [{"url":"","title":""},{}]

            request.session["permission_menu_list"]=permission_menu_list


            return redirect("/index/")


    return render(request,"login.html")

def index(request):


    return render(request,"index.html")














































# from django.shortcuts import render,redirect
#
# # Create your views here.
#
# from rbac.models import User
#
#
# #登录函数
# def login(request):
#    if request.method=="POST":
#        user=request.POST.get('user')
#        pwd=request.POST.get('pwd')
#
#        user=User.objects.filter(user=user,pwd=pwd).first()
#
#        if user:
#             #存储登录状态
#             request.session['user']=user.user
#             #查询当前登录用户的所有权限url
#
#             permissions=user.roles.all().values('permissions__url','permissions__code','permissions__title').distinct()
#
#             print(user.roles.all().values('permissions__url',88))
#
#             permission_list=[]  #是url集合
#             permission_menu_list=[]
#
#             for item in permissions:
#                 permission_list.append(item['permissions__url'])
#
#                 if item['permissions__code']=='list':
#                     permission_menu_list.append({
#                         'url':item['permissions__url'],
#                         'title':item['permissions__title']
#                     })
#                 print('permission_list',permission_list,99)
#
#                 #将权限列表存储到session中
#                 request.session['permission_list']=permission_list
#                 #将菜单权限列表注册到session中
#                 request.session['permission_menu_list']=permission_menu_list
#                 print("permission_menu_list", permission_menu_list,66)
#
#                 return redirect("/index/")
#
#        return render(request,'login.html')
#
#
#
# def index(request):
#     return render(request,'index.html')