from django.urls import path

from .views import *

urlpatterns = [
    path("", inbox_view, name="inbox"),
    path("conversation/<str:pk>", inbox_view, name="inbox"),
    path("search_users/", search_users, name="inbox-searchusers"),
    path("new_message/<int:pk>", new_message, name="inbox-newmessage"),
    path("new_reply/<str:pk>", new_reply, name="inbox-newreply"),
    path("notify/<str:pk>", notify_newmessage, name="notify-newmessage"),
    path("notify-inbox/", notify_inbox, name="notify-inbox"),
]
