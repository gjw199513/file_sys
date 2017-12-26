from django.shortcuts import render

from django.views.generic import View
from .models import Upload
from django.http import HttpResponsePermanentRedirect, HttpResponse
import random
import string
import json
import datetime
# Create your views here.


class HomeView(View):
    def get(self, request):
        return render(request, 'base.html', {})

    # post请求
    def post(self, request):
        # 如果有文件，向下执行，没有文件的情况，前端已经处理好
        if request.FILES:
            # 获取文件，在html中的name为file的file输入框中
            file = request.FILES.get("file")
            # 获取文件名
            name = file.name
            # 获取文件大小
            size = int(file.size)
            # 写文件到static/files
            with open('static/file/'+name, 'wb')as f:
                f.write(file.read())
            # 生成随机八位的code
            code = ''.join(random.sample(string.digits, 8))
            u = Upload(
                path='static/file/'+name,
                name=name,
                Filesize=size,
                code=code,
                # 获取上传文件的用户ip
                PCIP=str(request.META['REMOTE_ADDR']),
            )
            u.save()
            # 使用 HttpResponsePermanentRedirect 重定向到展示文件的页面.这里的 code 唯一标示一个文件。
            return HttpResponsePermanentRedirect('/s/'+code)


class DisplayView(View):  # 展示文件的视图类
    def get(self, request, code):  # 支持get请求,并且可接受一个参数，这里的code 需要和 配置路由的 code 保持一致
        u = Upload.objects.filter(code=str(code))  # ORM 模型的查找
        if u:  # 如果u 有内容,u的访问次数+1，否则返回给前端的内容也是空的.
            for i in u:
                i.DownloadDocount += 1  # 每次访问,访问次数+1
                i.save()  # 保存结果
        return render(request, 'content.html', {"content": u})  # 返回页面,其中content是#我们传给前端页面的内容
        # content.html在template文件夹中。


class MyView(View):
    def get(self, request):
        # 获取用户ip
        IP = request.META['REMOTE_ADDR']
        # 查找数据
        u = Upload.objects.filter(PCIP=str(IP))
        for i in u:
            # 访问量+1
            i.DownloadDocount += 1
            i.save()
        return render(request, 'content.html', {'content': u})


class SearchView(View):
    def get(self, request):
        # 获取get请求中的kw的值，即搜索的内容
        code = request.GET.get("kw")
        u = Upload.objects.filter(name__icontains=str(code))
        data = {}
        if u:
            for i in range(len(u)):
                # 将符合条件的数据放到data中
                u[i].DownloadDocount += 1
                u[i].save()
                data[i] = {}
                data[i]['download'] = u[i].DownloadDocount
                data[i]['filename'] = u[i].name
                data[i]['id'] = u[i].id
                data[i]['ip'] = str(u[i].PCIP)
                data[i]['size'] = str(u[i].PCIP)
                # 时间格式化
                data[i]['time'] = str(u[i].Datatime.strftime('%Y-%m-%d %H:%M'))
                data[i]['key'] = u[i].code
                # django使用HttpResponse返回json的标准方式，content_type是标准写法
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')