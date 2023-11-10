from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Count

from a_posts.forms import ReplyCreateForm
from a_inbox.forms import InboxNewMessageForm
from .forms import *


def profile_view(request, username: str = None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            raise Http404()

    posts = profile.user.posts.all()
    if request.htmx:
        if "top-posts" in request.GET:
            posts = (
                profile.user.posts.annotate(num_likes=Count("likes"))
                .filter(num_likes__gt=0)
                .order_by("-num_likes")
            )

            template = "snippets/loop_profile_posts.html"
            context = {"posts": posts}
        elif "top-comments" in request.GET:
            comments = (
                profile.user.comments.annotate(num_likes=Count("likes"))
                .filter(num_likes__gt=0)
                .order_by("-num_likes")
            )

            template = "snippets/loop_profile_comments.html"
            context = {"comments": comments, "reply_form": ReplyCreateForm()}
        elif "liked-posts" in request.GET:
            posts = profile.user.likedposts.order_by("-likedpost__created")

            template = "snippets/loop_profile_posts.html"
            context = {"posts": posts}
        else:
            template = "snippets/loop_profile_posts.html"
            context = {"posts": posts}

        return render(request, template, context)

    context = {
        "profile": profile,
        "posts": posts,
        "new_message_form": InboxNewMessageForm(),
    }
    return render(request, "a_users/profile.html", context)


@login_required
def profile_edit_view(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")

    if request.path == reverse("profile-onboarding"):
        template = "a_users/profile_onboarding.html"
    else:
        template = "a_users/profile_edit.html"

    return render(request, template, {"form": form})


@login_required
def profile_delete_view(request):
    user = request.user

    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, "Account deleted, what a pity")
        return redirect("home")

    return render(request, "a_users/profile_delete.html")
