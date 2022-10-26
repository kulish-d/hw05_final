from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from yatube.settings import ELEMENTS_MAX_COUNT
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


def get_page(request, post_list):
    return (Paginator(post_list, ELEMENTS_MAX_COUNT)
            .get_page(request.GET.get('page')))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': get_page(request, Post.objects.all()),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_page(request, group.posts.all()),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author__following__user=request.user).exists()
    else:
        following = False
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': get_page(request, author.posts.all()),
        'following': following,
    })


def post_detail(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': form,
        'comments': post.comments.all(),
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:profile', post.author)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form,
            'is_edit': True
        })
    form.save()
    return redirect('posts:post_detail', post.id)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(id=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': get_page(
            request, Post.objects.filter(
                author__following__user=request.user
            ).all()
        )
    })


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user and not Follow.objects.filter(
        user=user,
        author=author
    ).exists():
        Follow.objects.create(
            user=user,
            author=author
        )
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user and Follow.objects.filter(
        user=user,
        author=author
    ).exists():
        Follow.objects.get(
            user=user,
            author=author
        ).delete()
    return redirect('posts:index')
