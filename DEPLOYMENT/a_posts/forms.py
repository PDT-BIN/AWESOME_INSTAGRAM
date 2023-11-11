from django import forms

from .models import *


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["url", "body", "tags"]
        labels = {"body": "Caption", "tags": "Category"}
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Add a caption...",
                    "class": "font1 text-4xl",
                }
            ),
            "url": forms.TextInput(attrs={"placeholder": "Add a url..."}),
            "tags": forms.CheckboxSelectMultiple(),
        }


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["body", "tags"]
        labels = {"body": "Caption", "tags": "Category"}
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Add a caption...",
                    "class": "font1 text-4xl",
                }
            ),
            "url": forms.TextInput(attrs={"placeholder": "Add a url..."}),
            "tags": forms.CheckboxSelectMultiple(),
        }


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {"body": ""}
        widgets = {"body": forms.TextInput(attrs={"placeholder": "Add comment..."})}


class ReplyCreateForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["body"]
        labels = {"body": ""}
        widgets = {
            "body": forms.TextInput(
                attrs={"placeholder": "Add reply...", "class": "!text-sm"}
            )
        }
