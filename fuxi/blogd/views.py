from django.shortcuts import render,get_object_or_404
from blogd.models import Post,Comment
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.views.generic import ListView
from blogd.forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
# ,Avg,Max,Min

# Create your views here.
# FBV函数视图
# CBV 类视图

class PostListView(ListView):
    # queryset 查询所有已经发布的文章
    # 可以不用queryset,通过指定model=Post， 会进行post.objects.all()查询获得所有的文章
    # model = Post
    queryset = Post.published.all()
    # 设置posts为模板变量的名称，不过不设置，默认的名称就是objects_list
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blogd/post/list.html'
    #返回分页的变量名称是page_obj

def post_list(request,tag_slug=None):
    posts = Post.published.all()
    print(posts)
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag,slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    # 每页显示两篇文章
    paginator = Paginator(posts,2)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    # 如果不是整数类型显示第一页
    except PageNotAnInteger:
        posts = paginator.page(1)
    # 如果超出总页数就显示最后一页
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request,'blogd/post/list.html',{'posts':posts,'page':page,'tag':tag})


def post_detail(request,year,month,day,slug):
    post = get_object_or_404(Post,slug=slug,status='publish',publish__year=year,
                             publish__month=month,publish__day=day)
    # 列出文章中所有活跃的评论
    comment = post.comments.filter(active=True)

    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # 通过表单直接创建新的数据对象，但是不保存在数据库中
            new_comment = comment_form.save(commit=False)
            # 设置外键为当前文章
            new_comment.post = post
            # 最后将评论写入数据库中
            new_comment.save()
    else:
        comment_form = CommentForm()

    # 显示相近的tag文章列表
    # flat = True 让结果变成一个列表
    post_tags_ids = post.tags.values_list('id',flat=True)
    similar_tags = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # 使用count对每个文章按照标签计数，并且生成一个新的字段same_tags用于存放计数的结果
    similar_posts = similar_tags.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:2]
    return render(request,'blogd/post/detail.html',{'post':post,
                                                    'comments':comment,
                                                    'new_comment':new_comment,
                                                    'comment_form':comment_form,
                                                    'similar_posts':similar_posts
                                                    })

def post_share(request,post_id):
    # 通过id获取post对象
    post = get_object_or_404(Post,id=post_id,status='publish')
    send = False
    if request.method =='POST':
        # 表单被提交
        form = EmailPostForm(request.POST)
        # 如果返回false.form.errors
        if form.is_valid():
            # 验证表单数据
            cd = form.cleaned_data
            # 发送邮件
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} share reding'.format(cd['name'])
            message = 'read comments {},文章的链接是{}'.format(cd['comments'],post_url)
            send_mail(subject,message,cd['email'],[cd['to']])
            send = True
    else:
        # 创建一个空白的form对象，展示在页面中是一个空白的表单供用户去填写
        form = EmailPostForm()

    return render(request,'blogd/post/share.html',{'post':post,'form':form,'send':send})