from django.shortcuts import render, get_object_or_404,redirect
import markdown
import re
from markdown.extensions.toc import TocExtension
# Create your views here.
from .models import Post,Tag,Category,UserInfo
from django.utils.text import slugify
from django.views.generic import ListView,DetailView
from django.core.paginator import Paginator
from pure_pagination import PaginationMixin
from django.contrib import messages
from django.db.models import Q

from .forms import UserForm, RegisterForm
# def index(request):
#
#     post_list = Post.objects.all()
#     return render(request,'blog/index.html',context={'post_list': post_list})

class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    #一页多少条数据
    paginate_by = 10

# def category(request, pk):
#
#     cate = get_object_or_404(Category, pk=pk)
#     post_list = Post.objects.filter(category=cate)
#     return render(request, 'blog/index.html', context={'post_list': post_list})

class CategoryView(IndexView):

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)

# def detail(request,pk):
#
#     post = get_object_or_404(Post, pk=pk)
#     md = markdown.Markdown(extensions=[
#         'markdown.extensions.extra',
#         'markdown.extensions.codehilite',
#         # 'markdown.extensions.toc',
#         TocExtension(slugify=slugify),
#     ])
#     post.increase_views()
#     post.body = md.convert(post.body)
#
#     m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
#     post.toc = m.group(1) if m is not None else ''
#
#     return render(request, 'blog/detail.html',context={'post': post})

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        self.object.increase_views()

        return response

    # def get_object(self, queryset=None):
    #
    #     post = super().get_object(queryset=None)
    #     md = markdown.Markdown(extensions=[
    #         'markdown.extensions.extra',
    #         'markdown.extensions.codehilite',
    #         # 'markdown.extensions.toc',
    #         TocExtension(slugify=slugify),
    #     ])
    #     post.body = md.convert(post.body)
    #
    #     m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    #     post.toc = m.group(1) if m is not None else ''
    #     return post

class ArchiveView(IndexView):

    def get_queryset(self):
        return super(ArchiveView,self).get_queryset().\
            filter(created_time__year=self.kwargs.get('year'),created_time__month=self.kwargs.get('month'))

# def archive(request, year, month):
#
#     post_list = Post.objects.filter(created_time__year=year,
#                                     created_time__month=month
#                                     )
#
#     return render(request, 'blog/index.html', context={'post_list': post_list})

class TagView(IndexView):

    def get_queryset(self):
        t = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=t)

# def tag(request, pk):
#
#     t = get_object_or_404(Tag, pk=pk)
#     post_list = Post.objects.filter(tags=t)
#     return render(request, 'blog/index.html', context={'post_list': post_list})


# def author(request,username):
#     post_list = Post.objects.filter(author__username=username)
#     return render(request, 'blog/index.html', context={'post_list': post_list})

class AuthorView(IndexView):

    def get_queryset(self):
        return super(AuthorView, self).get_queryset().filter(author__username=self.kwargs.get('username'))

def search(request):
    q = request.GET.get('q')

    if not q:
        error_msg = "请输入搜索关键词"
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'post_list': post_list})

def login(request):
    if request.session.get('is_login',None):
        return redirect('/')

    if request.method == "POST":
        login_form = UserForm(request.POST)
        # username = request.POST.get('username', None)
        # password = request.POST.get('password', None)
        message = "请检查填写的内容！"
        if login_form.is_valid():  # 确保用户名和密码都不为空
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            # username = username.strip()
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....
            try:
                user = UserInfo.objects.get(username=username)
                # if user.password == password:
                if user.check_password(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    return redirect('/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request, 'login/login.html', {"message": message, "login_form": login_form})
    login_form = UserForm()
    return render(request, 'login/login.html', {"login_form": login_form})


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/")


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            gender = register_form.cleaned_data['gender']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = UserInfo.objects.filter(username=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = UserInfo.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = UserInfo.objects.create()
                new_user.username = username
                new_user.password = password1
                new_user.email = email
                new_user.gender = gender
                new_user.save()
                return redirect('/login/', {'message': '注册成功，请登录'})  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())