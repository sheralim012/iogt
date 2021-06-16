import json
import uuid
from urllib import request, parse

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView,
    DeleteView,
    TemplateView,
    UpdateView,
)

from .forms import MessageReplyForm, NewMessageForm, NewMessageFormMultiple
from .models import Thread, Message

try:
    from account.decorators import login_required
except:  # noqa
    from django.contrib.auth.decorators import login_required


class InboxView(TemplateView):
    """
    View inbox thread list.
    """
    template_name = "messaging/inbox.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get("deleted", None):
            threads = Thread.ordered(Thread.deleted(self.request.user))
            folder = "deleted"
        else:
            threads = Thread.ordered(Thread.inbox(self.request.user))
            folder = "inbox"

        context.update({
            "folder": folder,
            "threads": threads,
            "threads_unread": Thread.ordered(Thread.unread(self.request.user))
        })
        return context



class ThreadView(UpdateView):
    """
    View a single Thread or POST a reply.
    """
    model = Thread
    form_class = MessageReplyForm
    context_object_name = "thread"
    template_name = "messaging/thread_detail.html"
    success_url = reverse_lazy("messaging:inbox")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(userthread__user=self.request.user).distinct()
        return qs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "user": self.request.user,
            "thread": self.object
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.userthread_set.filter(user=request.user).update(unread=False)
        return response


class MessageCreateView(CreateView):
    """
    Create a new thread message.
    """
    template_name = "messaging/message_create.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_class(self):
        if self.form_class is None:
            if self.kwargs.get("multiple", False):
                return NewMessageFormMultiple
        return NewMessageForm

    def get_initial(self):
        user_id = self.kwargs.get("user_id", None)
        if user_id is not None:
            user_id = [int(user_id)]
        elif "to_user" in self.request.GET and self.request.GET["to_user"].isdigit():
            user_id = map(int, self.request.GET.getlist("to_user"))
        if not self.kwargs.get("multiple", False) and user_id:
            user_id = user_id[0]
        return {"to_user": user_id}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "user": self.request.user,
        })
        return kwargs


class ThreadDeleteView(DeleteView):
    """
    Delete a thread.
    """
    model = Thread
    success_url = reverse_lazy("messaging:inbox")
    template_name = "messaging/thread_confirm_delete.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.userthread_set.filter(user=request.user).update(deleted=True)
        return HttpResponseRedirect(success_url)


# @csrf_exempt is a temp fix to make things work,
# see https://stackoverflow.com/questions/17716624/django-csrf-cookie-not-set
# TODO: Implement a secure(?) solution.
@csrf_exempt
def rapidpro_interface(request):
    if not request.method == 'POST':
        # TODO: What exactly to do in this case.
        return HttpResponse("Bad request.")
    # TODO: Check other header info, such as auth token, content type.

    fields = json.loads(request.body.decode("utf-8"))
    msg_id = fields.get('id')
    content = fields.get('text')
    thread_uuid = fields.get('to')
    bot_identifier = fields.get('from')  # currently unused
    channel_uuid = fields.get('channel')
    quick_replies = fields.get('quick_replies')

    # TODO: Decide how to treat each of these potential errors:
    # - Invalid thread UUID
    # - channel UUID mismatch
    thread = Thread.objects.get(uuid=uuid.UUID(thread_uuid))
    assert uuid.UUID(channel_uuid) == thread.chatbot.channel_uuid()
    
    # TODO(geoo89): Look for messages with the same rapid_pro_message_id.
    # They are single messages in RapidPro that got split up and we need
    # to stitch them back together.
    # msg_parts = Message.objects.filter(thread=thread, rapid_pro_message_id=msg_id)
    # TODO(geoo89): Extract attachments from messages.

    Message.new_reply(
            thread, None, content,
            sent_from_bot=True,
            rapid_pro_message_id=msg_id,
            quick_replies=json.dumps(quick_replies))

    # When defining a channel in RapidPro, we can specify a string
    # that the response should contain for RapidPro to consider the
    # message as successfully delivered.
    return HttpResponse("All Good.")
