from django.shortcuts import render
from .models import Post
from django.http import HttpResponseNotFound


def post_list(request):
    posts = Post.published.all()
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, id):
    try:
        post = Post.published.get(id=id)
    except Post.DoesNotExist:
        return HttpResponseNotFound("Post not found")
    return render(request, 'blog/post/detail.html', {'post': post})