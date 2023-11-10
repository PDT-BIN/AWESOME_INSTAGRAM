from django.http import HttpResponse, Http404
from django.db.models import Q
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from cryptography.fernet import Fernet

from .models import *
from .forms import *


f = Fernet(settings.ENCRYPT_KEY)


@login_required
def inbox_view(request, pk: str = None):
    conversations = request.user.conversations.all()
    if pk:
        conversation = get_object_or_404(Conversation, pk=pk)
        latest_message = conversation.messages.first()
        if not conversation.is_seen and latest_message.sender != request.user:
            conversation.is_seen = True
            conversation.save()
    else:
        conversation = None

    context = {"conversation": conversation, "conversations": conversations}
    return render(request, "a_inbox/inbox.html", context)


@login_required
def search_users(request):
    letters = request.GET.get("search_user")

    if request.htmx:
        if letters:
            users = User.objects.filter(
                Q(username__istartswith=letters)
                | Q(profile__realname__icontains=letters)
            ).exclude(username=request.user.username)
            return render(request, "a_inbox/list_searchusers.html", {"users": users})
        else:
            return HttpResponse("")
    else:
        raise Http404()


@login_required
def new_message(request, pk: str):
    recipient = get_object_or_404(User, pk=pk)
    new_message_form = InboxNewMessageForm()

    if request.method == "POST":
        form = InboxNewMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)

            # ENCRYPT MESSAGE.
            original_message: str = form.cleaned_data["body"]
            encoded_message = original_message.encode()
            encrypted_message = f.encrypt(encoded_message)
            decoded_message = encrypted_message.decode()

            message.body = decoded_message
            message.sender = request.user

            for c in request.user.conversations.all():
                if recipient in c.participants.all():
                    message.conversation = c
                    message.save()

                    c.lastmessage_created = timezone.now()
                    c.is_seen = False
                    c.save()

                    return redirect("inbox", c.pk)

            new_conversation = Conversation.objects.create()
            new_conversation.participants.add(request.user, recipient)
            new_conversation.save()

            message.conversation = new_conversation
            message.save()

            return redirect("inbox", new_conversation.pk)

    context = {"recipient": recipient, "new_message_form": new_message_form}
    return render(request, "a_inbox/form_newmessage.html", context)


@login_required
def new_reply(request, pk: str):
    new_message_form = InboxNewMessageForm()
    my_conversations = request.user.conversations.all()
    conversation = get_object_or_404(Conversation, pk=pk)

    if request.method == "POST":
        form = InboxNewMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)

            # ENCRYPT MESSAGE.
            original_message: str = form.cleaned_data["body"]
            encoded_message = original_message.encode()
            encrypted_message = f.encrypt(encoded_message)
            decoded_message = encrypted_message.decode()

            message.body = decoded_message
            message.sender = request.user
            message.conversation = conversation
            message.save()

            conversation.lastmessage_created = timezone.now()
            conversation.is_seen = False
            conversation.save()
            return redirect("inbox", conversation.pk)

    context = {
        "conversation": conversation,
        "conversations": my_conversations,
        "new_message_form": new_message_form,
    }
    return render(request, "a_inbox/form_newreply.html", context)


@login_required
def notify_newmessage(request, pk: str):
    conversation = get_object_or_404(Conversation, pk=pk)
    latest_message = conversation.messages.first()

    if not conversation.is_seen and latest_message.sender != request.user:
        return render(request, "a_inbox/notify_icon.html")
    else:
        return HttpResponse("")


@login_required
def notify_inbox(request):
    my_conversations = request.user.conversations.filter(is_seen=False)
    for c in my_conversations:
        latest_message = c.messages.first()
        if latest_message.sender != request.user:
            return render(request, "a_inbox/notify_icon.html")
    return HttpResponse("")
