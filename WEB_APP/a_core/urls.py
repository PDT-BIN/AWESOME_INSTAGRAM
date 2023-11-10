from django.conf import settings
from django.conf.urls.static import static as url_static
from django.contrib import admin
from django.urls import include, path

from a_posts.views import *
from a_users.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("inbox/", include("a_inbox.urls")),
    path("", home_view, name="home"),
    path("category/<str:tag>", home_view, name="category"),
    path("post/create/", post_create_view, name="post-create"),
    path("post/delete/<str:pk>", post_delete_view, name="post-delete"),
    path("post/edit/<str:pk>", post_edit_view, name="post-edit"),
    path("post/<str:pk>", post_page_view, name="post"),
    path("profile/", profile_view, name="profile"),
    path("<str:username>/", profile_view, name="userprofile"),
    path("profile/edit/", profile_edit_view, name="profile-edit"),
    path("profile/delete/", profile_delete_view, name="profile-delete"),
    path("profile/onboarding/", profile_edit_view, name="profile-onboarding"),
    path("commentsent/<str:pk>", comment_sent, name="comment-sent"),
    path("comment/delete/<str:pk>", comment_delete_view, name="comment-delete"),
    path("replysent/<str:pk>", reply_sent, name="reply-sent"),
    path("reply/delete/<str:pk>", reply_delete_view, name="reply-delete"),
    path("post/like/<str:pk>", like_post, name="like-post"),
    path("comment/like/<str:pk>", like_comment, name="like-comment"),
    path("reply/like/<str:pk>", like_reply, name="like-reply"),
]

urlpatterns += url_static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
