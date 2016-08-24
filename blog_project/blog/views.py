# -*- coding:utf-8 -*-
import logging
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.db.models import Count
from models import *
from forms import *
import json

logger = logging.getLogger('blog.views')

def global_setting(req):
    #站点基本信息
    SITE_URL = settings.SITE_URL
    SITE_NAME = settings.SITE_NAME
    SITE_DESC = settings.SITE_DESC
    #导航信息
    category_list = Category.objects.all()[:6]
    #文章归档数据
    archive_list = Article.objects.distinct_date()
    #广告数据
    ad_list = Ad.objects.all()[:4]
    #标签运数据
    tag_list = Tag.objects.all()
    #友情连接数据
    link_list = Links.objects.all()
    #文章排行榜数据
    click_count_list = Article.objects.all().order_by('-click_count')[:5]
    #站长推荐
    recommend_list = Article.objects.filter(is_recommend=1)

    #评论排行
    comment_count_list = Comment.objects.values('article').annotate(comment_count=Count('article')).order_by('-comment_count')
    article_comment_list = [Article.objects.get(pk=comment['article']) for comment in comment_count_list]
    return locals()

def archive(req):
    try:
        #获取客户端提交的信息
        year = req.GET.get('year',None)
        month = req.GET.get('month',None)
        article_list = getPage(req,Article.objects.filter(date_publish__icontains=year+'-'+month))
    except Exception as e:
        logger.error(e)
    return render(req, 'archive.html', locals())
#安标签查询对应的文章列表
def tag(req):
    try:
        id = req.GET.get('id',None)
        tag = Tag.objects.get(id=id)
        article_list = tag.article_set.all()
        article_list = getPage(req,article_list)

    except Exception as e:
        logger.error(e)
    return render(req, 'tag.html', locals())

def article(req):
    try:
        id = req.GET.get('id',None)
        try:
            article = Article.objects.get(pk=id)
        except Article.DoesNotExist:
            return render(req, 'failure.html', {'reason': '没找到对应的文章'})

        comment_form = CommentForm({'author':req.user.username,
                                    'email':req.user.email,
                                    'url':req.user.url,
                                    'article':id} if req.user.is_authenticated() else{'article':id})
        #后去评论信息
        comments = Comment.objects.filter(article=article).order_by('id')
        comment_list = []
        for comment in comments:
            if comment.pid is None:
                comment_list.append(comment)
            for item in comment_list:
                if not hasattr(item,'children_comment'):
                    setattr(item,'children_comment',[])
                if comment.pid_id == item.id:
                    item.children_comment.append(comment)
                    break
    except Exception as e:
        print e
        logger.error(e)

    return render(req,'article.html',locals())

def comment_post(req):
    try:
        comment_form = CommentForm(req.POST)
        if comment_form.is_valid():
            #获取表单信息
            comment = Comment.objects.create(username=comment_form.cleaned_data["author"],
                                             email=comment_form.cleaned_data["email"],
                                             url=comment_form.cleaned_data["url"],
                                             content=comment_form.cleaned_data["comment"],
                                             article_id=comment_form.cleaned_data["article"],
                                             user=req.user if req.user.is_authenticated() else None)
            comment.save()
        else:
            return render(req, 'failure.html', {'reason': comment_form.errors})
    except Exception as e:
        logger.error(e)
    return redirect(req.META['HTTP_REFERER'])

# 注销
def do_logout(req):
    try:
        logout(req)
    except Exception as e:
        print e
        logger.error(e)
    return redirect(req.META['HTTP_REFERER'])

# 注册
def do_reg(req):
    try:
        if req.method == 'POST':
            reg_form = RegForm(req.POST)
            if reg_form.is_valid():
                # 注册
                user = User.objects.create(username=reg_form.cleaned_data["username"],
                                    email=reg_form.cleaned_data["email"],
                                    url=reg_form.cleaned_data["url"],
                                    password=make_password(reg_form.cleaned_data["password"]),)
                user.save()

                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                login(req, user)
                return redirect(req.POST.get('source_url'))
            else:
                return render(req, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()
    except Exception as e:
        logger.error(e)
    return render(req, 'reg.html', locals())

# 登录
def do_login(req):
    try:
        if req.method == 'POST':
            login_form = LoginForm(req.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(req, user)
                else:
                    return render(req, 'failure.html', {'reason': '登录验证失败'})
                return redirect(req.POST.get('source_url'))
            else:
                return render(req, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(req, 'login.html', locals())

def index(req):
    try:
        #最新文章数据
        article_list = getPage(req,Article.objects.all())
    except Exception as e:
        print e
        logger.error(e)
    return render(req, 'index.html', locals())
def category(req):
    try:
        # 先获取客户端提交的信息
        cid = req.GET.get('cid', None)
        try:
            category = Category.objects.get(pk=cid)
        except Category.DoesNotExist:
            return render(req, 'failure.html', {'reason': '分类不存在'})
        article_list = Article.objects.filter(category=category)
        article_list = getPage(req, article_list)
    except Exception as e:
        logger.error(e)
    return render(req, 'category.html', locals())

def getPage(req,article_list):
    paginator = Paginator(article_list, 2)
    try:
        page = int(req.GET.get('page', 1))
        article_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list

# Create your views here.
