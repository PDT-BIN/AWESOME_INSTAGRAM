from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from django.db.models import Count
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import *
from .models import *


def home_view(request, tag: str = None):
    posts = Post.objects.all()

    if tag:
        posts = posts.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)

    paginator = Paginator(posts, 3)
    page = int(request.GET.get("page", 1))

    try:
        posts = paginator.page(page)
    except:
        return HttpResponse("")

    context = {"posts": posts, "tag": tag, "page": page}

    if request.htmx:
        return render(request, "snippets/loop_home_posts.html", context)

    return render(request, "a_posts/home.html", context)


@login_required
def post_create_view(request):
    form = PostCreateForm()

    if request.method == "POST":
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # REQUEST THE URL.
            website = requests.get(form.data["url"])
            # PARSE THE CONTENT OF WEBSITE TO HTML FORMAT.
            sourcecode = BeautifulSoup(website.text, "html.parser")
            # SELECT NECCESSARY INFORMATION.
            find_image = sourcecode.select(
                'meta[content^="https://live.staticflickr.com/"]'
            )
            find_title = sourcecode.select("h1.photo-title")
            find_artist = sourcecode.select("a.owner-name")
            # TRY GET INFORMATIONS.
            try:
                image = find_image[0]["content"]
                title = find_title[0].text.strip()
                artist = find_artist[0].text.strip()
            except:
                pass
            # ASSIGN THOSE INFORMATIONS TO POST OBJECT.
            else:
                post.image = image
                post.title = title
                post.artist = artist
            post.author = request.user

            post.save()
            form.save_m2m()
            return redirect("home")

    return render(request, "a_posts/post_create.html", {"form": form})


@login_required
def post_delete_view(request, pk: str):
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted")
        return redirect("home")

    return render(request, "a_posts/post_delete.html", {"post": post})


@login_required
def post_edit_view(request, pk: str):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    form = PostEditForm(instance=post)

    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated")
            return redirect("home")

    context = {"post": post, "form": form}
    return render(request, "a_posts/post_edit.html", context)


def post_page_view(request, pk: str):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentCreateForm()
    reply_form = ReplyCreateForm()

    if request.htmx:
        if "top" in request.GET:
            # comments = post.comments.filter(likes__isnull=False).distinct()
            comments = (
                post.comments.annotate(num_likes=Count("likes"))
                .filter(num_likes__gt=0)
                .order_by("-num_likes")
            )
        else:
            comments = post.comments.all()

        context = {"comments": comments, "reply_form": reply_form}
        return render(request, "snippets/loop_postpage_comments.html", context)

    context = {"post": post, "comment_form": comment_form, "reply_form": reply_form}
    return render(request, "a_posts/post_page.html", context)


@login_required
def comment_sent(request, pk: str):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post
            comment.save()

    context = {"post": post, "comment": comment, "reply_form": ReplyCreateForm()}
    return render(request, "snippets/add_comment.html", context)


@login_required
def comment_delete_view(request, pk: str):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted")
        return redirect("post", comment.parent_post.pk)

    return render(request, "a_posts/comment_delete.html", {"comment": comment})


@login_required
def reply_sent(request, pk: str):
    comment = get_object_or_404(Comment, pk=pk)

    if request.method == "POST":
        form = ReplyCreateForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent_comment = comment
            reply.save()

    context = {"reply": reply, "comment": comment, "reply_form": ReplyCreateForm()}
    return render(request, "snippets/add_reply.html", context)


@login_required
def reply_delete_view(request, pk: str):
    reply = get_object_or_404(Reply, pk=pk, author=request.user)

    if request.method == "POST":
        reply.delete()
        messages.success(request, "Reply deleted")
        return redirect("post", reply.parent_comment.parent_post.pk)

    return render(request, "a_posts/reply_delete.html", {"reply": reply})


def like_toggle(model):
    def inner_func(func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            instance = get_object_or_404(model, pk=kwargs.get("pk"))
            user_existed = instance.likes.filter(username=user.username).exists()

            if instance.author != user:
                if user_existed:
                    instance.likes.remove(user)
                else:
                    instance.likes.add(user)
            return func(request, instance)

        return wrapper

    return inner_func


@login_required
@like_toggle(Post)
def like_post(request, post: Post):
    return render(request, "snippets/likes.html", {"post": post})


@login_required
@like_toggle(Comment)
def like_comment(request, comment: Comment):
    return render(request, "snippets/likes_comment.html", {"comment": comment})


@login_required
@like_toggle(Reply)
def like_reply(request, reply: Reply):
    return render(request, "snippets/likes_reply.html", {"reply": reply})
