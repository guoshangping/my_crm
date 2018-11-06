from .models import *
from mysky.service.sites import site
from django.conf.urls import url
from mysky.service.sites import site,ModelMysky
from django.shortcuts import HttpResponse,redirect,render
from django.utils.safestring import mark_safe
from django.http import JsonResponse



site.register(School)
site.register(Order)
site.register(UserInfo)

class ClassConfig(ModelMysky):
    list_display = ['course','semester','teachers','tutor']
site.register(ClassList,ClassConfig)


class CustomerConfig(ModelMysky):
    def display_gender(self,obj=None,is_header=False):
        if is_header:
            return "性别"
        return obj.get_gender_display()  #表字段（1，"男"） #取到男


    def display_course(self,obj=None,is_header=False):
        if is_header:
            return '咨询课程'


        link_list=[]
        for course in obj.course.all():  #和course是多对多的关系 ，查询需要对象.字段.all(),得到课程表的对象

            s="<a>%s</a>"%course.name
            link_list.append(s)
        return mark_safe("".join(link_list))  #不要转意，转成字符串  没有mark_safe列表里显示<a>python</a>
        # return mark_safe(link_list)   #['python']
    list_display = ['name',display_gender,'consultant',display_course]


site.register(Customer,CustomerConfig)


class StudentConfig(ModelMysky):
    def display_score(self,obj=None,is_header=False):
        if is_header:
            return "详细信息"
        return mark_safe("<a href='/mysky/app01/student/%s/info/'>详细信息</a>"%obj.pk)


    def student_info(self,request,sid):
        print(123)
        if request.is_ajax():
            cid=request.GET.get("cid")

            #查询学生sid在班级cid下的所有学生学习记录对象

            studentstudyrecord_list=StudentStudyRecord.objects.filter(student_id=sid,classstudyrecord__class_obj=cid) #跨表查询
            ret=[["day%s"%studentstudyrecord.classstudyrecord.day_num,studentstudyrecord.score] for studentstudyrecord in studentstudyrecord_list]
            print(ret)  ## [['day90', 100], ['day91', 80], ['day94', 80]]
            return JsonResponse(ret,safe=False)# 非字典类型不能序列化
        print("cid",11)
        student_obj=Student.objects.filter(pk=sid).first()
        class_list=student_obj.class_list.all()

        return render(request,"student_info.html",locals())

    def extra_url(self):
        temp=[]
        temp.append(url("(\d+)/info/",self.student_info))
        return temp
    print(55)
    list_display = ['customer',"class_list",display_score]

site.register(Student,StudentConfig)

site.register(ConsultRecord)




class ClassStudyRecordConfig(ModelMysky):
    def display_info(self,obj=None,is_header=False):  #自定义列，详细信息，设置a标签，需要调转到学生学习记录页面
        if is_header:
            return '详细信息'
        #告诉django不转译
        return mark_safe("<a href='/mysky/app01/studentstudyrecord/?classstudyrecord=%s'>详细信息</a>"%obj.pk)

    list_display = ["class_obj","day_num","teacher","homework_title",display_info]

    def batch_init(self,request,queryset):    #班级queryset

        for cls_study_obj in queryset:

           #查询班级关联的学生
            student_list=cls_study_obj.class_obj.student_set.all()  #反向student_set ，查询得到班级学习记录相关的学生对象
            ssr_list=[]  #学生学习记录
            for student in student_list:  #和班级学习记录相关的学生
                ssr =StudentStudyRecord(student=student,classstudyrecord=cls_study_obj) #学生学习记录表里字段与班级学习记录表生成的对象关联相等，拿到关联记录
                ssr_list.append(ssr)

            ClassStudyRecord.objects.bulk_create(ssr_list)

    batch_init.desc="创建关联学生学习记录"
    action=[batch_init]

site.register(ClassStudyRecord,ClassStudyRecordConfig)




class StudentStudyRecordConfig(ModelMysky):
    def edit_record(self,request,id):
        record=request.POST.get('record')
        StudentStudyRecord.objects.filter(pk=id).update(record=record)

        return HttpResponse('世界你好')

    def extra_url(self):
        temp=[]
        temp.append(url(r"(\d+)/edit_record/$",self.edit_record),)
        return temp

    def display_record(self,obj=None,is_header=False):  #增加自定义列，
        if is_header:
            return"出勤"

        html="<select name='record' class='record' pk=%s>"%obj.pk
        for item in StudentStudyRecord.record_choices:   #(()) 出勤的5种况
            if obj.record==item[0]:  #其中的一种，
                option="<option selected value='%s'>%s</option>"%(item[0],item[1])  #item[0]显示修改了的出勤情况，不会回到默认
            else:
                option="<option value='%s'>%s</option>"%(item[0],item[1])  #即使编辑修改了，刷新了还是回到表里默认，已签到

            html+=option
        html+="</select>"

        return mark_safe(html)

    def display_score(self,obj=None,is_header=False):  #动态的需要自定义列，
        if is_header:
            return "成绩"
        return obj.get_score_display()

    list_display=['student','classstudyrecord',display_record,display_score]

#设出勤状态一种方式
    def batch_late(self,request,queryset):  #可以通过action 来设置一批学生的出勤状态
        queryset.update(record="late")

    batch_late.desc="迟到"
    actions=[batch_late]


site.register(StudentStudyRecord,StudentStudyRecordConfig)

site.register(Department)
site.register(Course)

