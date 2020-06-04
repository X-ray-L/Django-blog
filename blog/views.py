from django.shortcuts import render, get_object_or_404,redirect
import markdown
import re
from markdown.extensions.toc import TocExtension
# Create your views here.
from .models import Post,Tag,Category
from django.utils.text import slugify
from django.views.generic import ListView,DetailView
from django.core.paginator import Paginator
from pure_pagination import PaginationMixin
from django.contrib import messages
from django.db.models import Q
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