from django.shortcuts import *
from .models import Post, Comment
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity, TrigramWordSimilarity


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    search_form = SearchForm()
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag, 'search_form': search_form, 'query': None})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)

    # Форма для комментариев пользователей
    form = CommentForm()

    # Список схожих постов
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})




def post_share(request, post_id):
    # Извлечь пост по его идентификатору id
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Форма была передана на обработку
        form_post = request.POST.copy()
        if request.user.is_authenticated:
            form_post['name'] = request.user.username
            form_post['email'] = request.user.email
        form = EmailPostForm(form_post)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f'{cd['name']} recommends you read "{post.title}"'
            message = f'Read "{post.title}" at {post_url}\n\n{cd['name']}\'s {f'({cd['email']})' if cd['email'] else ''} comments: {cd['comments']}'
            send_mail(subject, message, settings.EMAIL_HOST_USER,[cd['to']], fail_silently=False)
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    # Комментарий был отправлен
    comment_post = request.POST.copy()
    if request.user.is_authenticated:
        comment_post['name'] = request.user.username
        comment_post['email'] = request.user.email
    form = CommentForm(data=comment_post)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # Сохранить комментарий в базе данных
        comment.save()
    return HttpResponseRedirect(post.get_absolute_url())

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET and request.GET['query'].strip() != '':
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            A = 1.0
            B = 0.4
            results = Post.published.annotate(
                similarity=(A / (A + B) * TrigramSimilarity('title', query)
                            + B / (A + B) * TrigramWordSimilarity(query, 'body'))
            ).filter(similarity__gte=0.1).order_by('-similarity')

        return render(request, 'blog/post/list.html', {'posts': results,
                                                   'tag': None,
                                                   'search_form': form,
                                                   'query': query,
                                                   'is_search': True})
    else:
        return HttpResponseRedirect(reverse('blog:post_list'))

    # return render(request,
    #               'blog/post/search.html',
    #               {'form': form,
    #                'query': query,
    #                'results': results})
