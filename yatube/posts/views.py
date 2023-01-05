from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, User, Comment, Follow


def paginator(request, object):
    paginator = Paginator(object, settings.POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all().select_related("author")
    page_obj = paginator(request, post_list)
    template = "posts/index.html"
    context = {"page_obj": page_obj}
    return render(request, template, context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = group.group_list.all()
    page_obj = paginator(request, group_list)
    template = "posts/group_list.html"
    context = {"group": group, "page_obj": page_obj}
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_counter = author.posts.count()
    page_obj = paginator(request, post_list)
    template = "posts/profile.html"
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        "author": author,
        "post_counter": post_counter,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    title = post.text[:30]
    post_counter = post.author.posts.count()
    form = CommentForm()
    comments = Comment.objects.filter(post_id=post_id)
    template = "posts/post_detail.html"
    context = {
        "post": post,
        "post_counter": post_counter,
        "title": title,
        "form": form,
        "comments": comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    template = "posts/create_post.html"
    if not form.is_valid():
        return render(request, template, {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    template = "posts/create_post.html"
    context = {
        "title": "Редактировать запись",
        "form": form,
        "is_edit": True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    template = "posts/follow.html"
    context = {"page_obj": page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(user=user, author=author)
    if follow.exists():
        follow.delete()
    return redirect("posts:profile", username=username)
