from django.contrib.auth.models import User
from django.template import Library
from django.db.models import Count

from ..models import Tag, Post, Comment


register = Library()


@register.inclusion_tag("includes/sidebar.html")
def sidebar_view(tag: Tag = None, user: User = None):
    categories = Tag.objects.all()
    top_posts = (
        Post.objects.annotate(num_likes=Count("likes"))
        .filter(num_likes__gt=0)
        .order_by("-num_likes")
    )
    top_commnets = (
        Comment.objects.annotate(num_likes=Count("likes"))
        .filter(num_likes__gt=0)
        .order_by("-num_likes")
    )

    return {
        "categories": categories,
        "tag": tag,
        "top_posts": top_posts,
        "user": user,
        "top_comments": top_commnets,
    }
