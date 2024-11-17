from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()

# @register.inclusion_tag('blog/post/latest_posts.html')
# def show_latest_posts_and_most_commented_posts(count=5, count2=5):
#     latest_posts = Post.published.order_by('-publish')[:count]
#     commented_posts = Post.published.annotate(total_comments=Count('comments')).exclude(total_comments=0).order_by('-total_comments')[:count2]
#     return {'latest_posts': latest_posts, 'most_commented_posts': commented_posts}

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

@register.simple_tag
def get_latest_posts(count=5):
    return Post.published.order_by('-publish')[:count]


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).exclude(total_comments=0).order_by('-total_comments')[:count]