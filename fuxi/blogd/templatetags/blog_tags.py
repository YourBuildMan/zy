from django import template
from blogd.models import Post
from django.db.models import Count

# 用来注册一个自定义的标签
register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blogd/post/lastest_posts.html')
def show_lastest_posts(count=2):
    lastest_posts = Post.published.order_by('-publish')[:count]
    return {'lastest_posts':lastest_posts}

@register.simple_tag
def get_most_comment_posts():
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:2]

@register.filter
def post_add(num,noc):
    return num + noc

@register.filter
def post_jing(num):
    return str(num) + '精品认证1'