# https://github.com/guoshangping/my_crm.git

from django.conf.urls import url
from django.shortcuts import render,redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from mysky.page import MyPage
from app01.models import *
from django.db.models import Q
import copy


class ShowList(object):


    def __init__(self,config_obj,data_list,request):   #config_obj相当于ModelMysky类里面的self
        self.config_obj=config_obj
        self.data_list=data_list
        self.request=request


    #分页                #类对象实例化                                                    每页显示数据条数
        self.pagination=MyPage(request.GET.get('page',1),self.data_list.count(),request,per_page_data=4)
        self.page_queryset=self.data_list[self.pagination.start:self.pagination.end]

    def get_new_actions(self):

        temp=[]
        temp.extend(self.config_obj.actions)
        temp.append(self.config_obj.batch_delete)

        new_actions=[]
        # print(self.config_obj.actions)  #[path_init,patch_delete]

        for func in temp:
            new_actions.append({
                "text":func.desc,
                'name':func.__name__
            })

        return new_actions

        # 构建表头：
    def get_headers(self):
        # header_list=["书籍名称","价格","人民出版社"，"操作"]   默认配置类：    ["PUBLISH"]
        header_list = []
        for field_or_func in self.config_obj.new_list_display():  # 调用list_display静态属性，把值传进来
            if callable(field_or_func):  # 判断是否可调用，是方法或类
                val = field_or_func(self.config_obj, is_header=True)  #如果是方法或类就调用或实例化
            else:
                if field_or_func == '__str__':
                    val = self.config_obj.model._meta.model_name  # 表名转字符串
                else:
                    field_obj = self.config_obj.model._meta.get_field(field_or_func)  # 获取模型的字段
                    val = field_obj.verbose_name  # 获取model表里verbose_name中文名称

            header_list.append(val)

        return header_list

# 构建数据表单部分

    def get_body(self):

        new_data_list = []
        # for obj in self.data_list:
        for obj in self.page_queryset:
            # print(obj,88)   每本书名字
            temp = []
            for field_or_func in self.config_obj.new_list_display():  #
                # print(field_or_func,666)   得到list_display里的字段，或方法
                if callable(field_or_func):  # 是否是可调用的，函数和类都可以，返回bool值
                    val = field_or_func(self.config_obj, obj)  # 传obj,编辑才跳转到指定页面
                else:
                    try:
                        from django.db.models.fields.related import ManyToManyField
                        field_obj = self.config_obj.model._meta.get_field(field_or_func)  # 获取模型的字段
                        if isinstance(field_obj, ManyToManyField):  # 判断是否是多对多字段
                            rel_data_list = getattr(obj, field_or_func).all()
                            # print(rel_data_list,55)   #作者的对象集合

                            l = [str(item) for item in rel_data_list]  # 不转str 结果 app01.Author.None
                            val = ",".join(l)
                        else:  # 非多对多
                            val = getattr(obj, field_or_func)

                            if field_or_func in self.config_obj.list_display_links:
                                _url=self.config_obj.get_change_url(obj)
                                val=mark_safe("<a href='%s'>%s</a>"%(_url,val))

                    except Exception as e:  # __str__
                        val = getattr(obj, field_or_func)

                temp.append(val)

            new_data_list.append(temp)

        return new_data_list



    def get_list_filter_links(self):
        # print(self.config_obj.list_filter)  ['publish','authors']


        list_filter_links={}

        for field in self.config_obj.list_filter:
            params=copy.deepcopy(self.request.GET)
            current_field_pk=params.get(field,0)


            field_obj=self.config_obj.model._meta.get_field(field)   #得到表的字段
            rel_model=field_obj.rel.to    #拿到关联表的一个对象
            rel_model_queryset=rel_model.objects.all()    # #拿到关联表的所有对象
            # print('rel_model_querset',rel_model_queryset)

            temp=[]
            for obj in rel_model_queryset:
                params[field]=obj.pk
                if obj.pk==int(current_field_pk):
                    link="<a class='active' href='?%s'>%s</a>"%(params.urlencode(),str(obj))

                else:
                    link = "<a  href='?%s'>%s</a>"%(params.urlencode(), str(obj))

                temp.append(link)
            # list_filter_links.append(temp)
            list_filter_links[field]=temp
            # print(list_filter_links,880)

        return list_filter_links


class ModelMysky(object):   #默认配置类
#  属性
    list_display=["__str__"]   #表中要展示额字段    有自定义类用自己的，没有用默认的配置类中字段，publish和autor没有自定义类，默认的list_display属性又为空，表中只有publish和autor对象生成字段
    model_form_class=[]        #
    list_display_links=[]      #点击字体可以做编辑操作
    search_fields=[]
    actions=[]
    list_filter=[]
#以上这些在类里是属性，可以用对象调用，其实也是变量，可以当变量用

#
    def __init__(self,model): # 下面admin_class = ModelMysky------- self._registry[model]=admin_class(model)实例化传进来的
        self.model=model       #相当于 ModelMysky（）实例化，admin_class为none 时=
        self.model_name=self.model._meta.model_name
        self.app_label = self.model._meta.app_label


    def batch_delete(self,request,queryset):
        queryset.delete()
    batch_delete.desc="批量删除"


#反向解析当前查表的增删改查的url
    def get_list_url(self):
        url_name = "%s_%s_list" % (self.app_label,self.model_name)
        _url = reverse(url_name)
        return _url

    def get_add_url(self):
        url_name = "%s_%s_add" % (self.app_label,self.model_name)
        _url = reverse(url_name)
        return _url

    def get_change_url(self,obj):
        url_name = "%s_%s_change" % (self.app_label,self.model_name)
        _url = reverse(url_name,args=(obj.pk,))
        return _url


    def get_del_url(self,obj):
        url_name = "%s_%s_delete" % (self.app_label,self.model_name)
        _url = reverse(url_name,args=(obj.pk,))
        return _url


#默认操作函数
    def edit(self,obj=None,is_header=False):
        if is_header:
            return "编辑操作"

        else:
            # url_name = reverse('%s_%s_change'%(self.app_label,self.model_name))
            # _url=reverse(url_name,args=(obj.pk,))
            # # return mark_safe("<a href='/mysky/app01/book/%s/change/'>编辑</a>" % obj.pk)
            return mark_safe('<a href="%s">编辑</a>'% self.get_change_url(obj))


    def delete(self,obj=None,is_header=False):
        if is_header:
            return "删除操作"
        # else:
            # url_name = reverse('%s_%s_delete' % (self.app_label, self.model_name))
            # _url = reverse(url_name, args=(obj.pk,))
        return mark_safe('<a href="%s">删除</a>' % self.get_del_url(obj))

    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return "选择"


        return mark_safe('<input type="checkbox" name="pk_list" value=%s>'% obj.pk)   # checkbox中name名字与action中接受到的相同，起作用
                                                                # value=%s>'% obj.pk，和book表主键关联 。对象(obj).属性(pk)

    def new_list_display(self):
        temp=[]
        temp.extend(self.list_display)
        temp.insert(0,ModelMysky.checkbox)
        if not self.list_display_links:
            temp.append(ModelMysky.edit)
        temp.append(ModelMysky.delete)

        return temp

#search部分

    def get_search_condition(self,request):

        val =request.GET.get("q")
        search_condition = Q()
        if val:
            search_condition.connector="or"   #转成or条件
            for field in self.search_fields:
                search_condition.children.append((field +"__icontains",val))

        return search_condition



#filter 部分
    def get_filter_condition(self,request):

        filter_conditon=Q()

        for key,val in request.GET.items():
            if key in ['page','q']:   #告诉不处理分页和q
                continue
            filter_conditon.children.append((key,val))

        return filter_conditon



    def listview(self,request):

        print(self)  # 当前访问模型表的配置类对象
        # print(self.model)  #当前访问模型表


        if request.method=="POST":  #前端form表单通过post方法，
            pk_list=request.POST.getlist('pk_list')  #checkboxde name值为'pk_list'
            # print(888888,pk_list)  #['2']   得到选中checkbox，book表的id集合，
            queryset=self.model.objects.filter(pk__in=pk_list)  #django 有的方法，用self对象调用，不是本类中方法，筛选出选中了哪一条数据
            action=request.POST.get('action')  #select的name值 ，得到名字对象，是字符串
            # print("action",999)
            if action:   #判断是否有值，是否有选择
                action=getattr(self,action)  #因为得到名字对象，是字符串 ，用反射来操作
                action(request,queryset)





        add_url = self.get_add_url()
        data_list=self.model.objects.all()    #当前访问模型表的对象集合

        #获取搜索条件对象
        search_condition=self.get_search_condition(request)

        #获取filter decondition
        filter_condition=self.get_filter_condition(request)

      #数据过滤
        data_list=data_list.filter(search_condition).filter(filter_condition)


        #分页展示
        showlist=ShowList(self,data_list,request)

#分页
        # page_num = request.GET.get('page',1)
        # all_data_amount=data_list.count()
        # url=self.get_list_url()
        # page_obj=MyPage(page_num,url,all_data_amount,request,per_page_data=3)
        # new_page_list=new_data_list[page_obj.start:page_obj.end]


        return render(request,'mysky/list_view.html',locals()) #返回当前作用域变量的字典形式



#pop 弹框

#pop弹框，对增加或编辑form对象进一步操作
#判断是否是一对多，多对多字段，是就增加属性。前端加+
    def get_new_form(self,form):
        from django.forms.boundfield import BoundField
        from django.forms.models import ModelChoiceField    #在modelform组件中，关联字典判断需要依据ModelChoiceField类，
        for bfield in form:
            if isinstance(bfield.field,ModelChoiceField):
                print("...",type(bfield.field))
                bfield.is_pop= True  #加属性
                # print(bfield.name)

                # print(self.model._meta.get_field(bfield.name).rel.to,8)
                #关联表
                rel_model =self.model._meta.get_field(bfield.name).rel.to

                model_name=rel_model._meta.model_name
                app_label=rel_model._meta.app_label
                _url=reverse("%s_%s_add"%(app_label,model_name))  #执行add_view函数
                bfield.url=_url

                bfield.pop_back_id="id_"+bfield.name#字段名字

        return form



    def get_model_form(self):

        if self.model_form_class:    #得到表名字
            return self.model_form_class

        else:
            from django.forms import widgets as wid
            class ModelFormClass(forms.ModelForm):  #为了下面的
                class Meta:
                    model=self.model            #把数据库和表字段关联起来，下面验证之后存储时，
                    fields="__all__"           #不用查询数据库create,直接.save就添加成功了


            return ModelFormClass



    def addview(self,request):

        ModelFormClass = self.get_model_form()
        if request.method=='POST':

            form = ModelFormClass(request.POST)    #实例化modelform对象
            form = self.get_new_form(form)#错误是没有加号

            if form.is_valid():   #验证   ，form和modelform 都要验证，都有此方法
                obj=form.save()    #过滤成功，直接save,modelformd的方法，赋值给一个新的对象

                is_pop=request.GET.get("pop")

                if is_pop:    #判断如果是pop操作，返回中间操作html
                    text=str(obj)   #option 需要两个值，添加好的主键值和文本
                    pk=obj.pk

                    return render(request,'mysky/pop.html',locals())

                else:
                    return redirect(self.get_list_url())

            return render(request,"mysky/add_view.html",locals())

        form=ModelFormClass()
        form=self.get_new_form(form)

        return render(request,'mysky/add_view.html',locals())


    def changeview(self,request,id):

        ModelFormClass = self.get_model_form()
        # print(ModelFormClass,888)
        edit_obj = self.model.objects.get(pk=id)

        if request.method=='POST':
            form = ModelFormClass(data=request.POST,instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request,'mysky/change_view.html',locals())

        form=ModelFormClass(instance=edit_obj)
        return render(request,'mysky/change_view.html',locals())



    def delview(self,request,id):

        if request.method=="POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(self.get_list_url())

        list_url=self.get_list_url()
        return render(request,'mysky/del_view.html',locals())

    #设计url
    def extra_url(self):
        return []



#设计url
    def get_urls(self):   #二级路由
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        temp = [
            url(r"^$", self.listview,name="%s_%s_list"%(app_label,model_name)),
            url(r"add/$", self.addview,name="%s_%s_add"%(app_label,model_name)),
            url(r"(\d+)/change/$", self.changeview,name="%s_%s_change"%(app_label,model_name)),
            url(r"(\d+)/delete/$", self.delview,name="%s_%s_delete"%(app_label,model_name)),

        ]

        temp.extend(self.extra_url())
        return temp


    @property
    def urls(self):
        return self.get_urls(),None,None



class AdminSite(object):  #   mysky组件的全局类

    def __init__(self):
        self._registry = {}


    def register(self,model,admin_class=None):  #admin_class是注册时的默认参数

        if not admin_class:   # 为真进入if条件，
            admin_class = ModelMysky   #用默认配置类，
            #隐含：如果注册的时候传了值site.register(Book, BookConfig)，，admin_class有值，就用自己自定义的类BookConfig，
            #site.register(Publish)，没有传参，就用默认配置类ModelMysky，

        self._registry[model]=admin_class(model)   #后者，可能是自定义配置类对象，也可以是默认配置类对象，根据admin_class接受参数,
        # print(self._registry,8)#    实例化admin_class(model) ，把model参数传进ModelMysky中
#{<class 'app01.models.Book'>: <app01.mysky.BookConfig object at 0x0000000003E973C8>, <class 'app01.models.Publish'>: <mysky.service.sites.ModelMysky object at 0x0000000003E97400>} 8

        # print(self._registry[model],"++++++")
        # print(admin_class(model),"+++++++")

#帮助分析
    # x = 'hello'
    # dic = {}
    # dic[x] = "123"
    # print(dic)
    # {'hello': '123'}

    def get_urls(self):    #设置得到路由方法

        temp =[]

        for model,config_obj in self._registry.items():  #循环当前访问的模型表对象和默认或者自定义类对象
            # print('model',model,7)   #model <class 'app01.models.Book'> 7，当前访问的模型表
            # print('config_obj',config_obj,7) #config_obj <app01.mysky.BookConfig object at 0x0000000003E97400> 7
            model_name = model._meta.model_name  #得到表名，app名字的字符串形式str的方法，固定的，不能换
            app_label = model._meta.app_label    #url的前部分需要字符串形式
            temp.append(url(r"%s/%s/" % (app_label,model_name),config_obj.urls))   #(app01/book/，config_obj.get_urls(),None,None)
            #config_obj 是model的配置类对象，加url伪装属性，得到某个表的url （[],None,None）形式

        return temp

    # print(555)
    @property
    def urls(self):
        return self.get_urls(),None,None


site = AdminSite()








'''
temp=[

    #(1) url(r"app01/book/",BookConfig(Book).urls)
    #(2) url(r"app01/book/",(BookConfig(Book).get_urls(), None, None))
    #(3) url(r"app01/book/",([
                                    url(r"^$", BookConfig(Book).listview),    #二级路由
                                    url(r"add/$", BookConfig(Book).addview),
                                    url(r"(\d+)/change/$", BookConfig(Book).changeview),
                                    url(r"(\d+)/delete/$", BookConfig(Book).delview),
                             ], None, None))

    ###########

    # url(r"app01/publish/",([
                                    url(r"^$", ModelStark(Publish).listview),
                                    url(r"add/$",  ModelStark(Publish).addview),
                                    url(r"(\d+)/change/$",  ModelStark(Publish).changeview),
                                    url(r"(\d+)/delete/$",  ModelStark(Publish).delview),
                             ], None, None))


]

'''










