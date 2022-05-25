from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from django_comments_xtd.models import XtdComment
from wagtail.contrib.modeladmin.options import ModelAdminGroup, ModelAdmin, modeladmin_register

from .button_helpers import XtdCommentAdminButtonHelper
from .filters import FlaggedFilter
from .models import CannedResponse


class XtdCommentAdmin(ModelAdmin):
    model = XtdComment
    menu_label = 'All Comments'
    menu_icon = 'edit'
    list_display = ('comment', 'user', 'status', 'num_flags', 'num_replies', 'submit_date', 'view_live')
    list_filter = (FlaggedFilter, 'is_removed', 'is_public', 'submit_date',)
    form_fields_exclude = ('thread_id', 'parent_id', 'level', 'order', 'followup', 'nested_count',
                           'content_type', 'object_id', 'user_email', 'user_url')
    search_fields = ('comment',)
    list_export = (
        'comment', 'user', 'is_removed', 'is_public', 'num_flags', 'num_replies', 'status', 'submit_date', 'article',
        'article_url', 'article_language_code',
    )
    button_helper_class = XtdCommentAdminButtonHelper
    menu_order = 601

    def status(self, obj):
        if not obj.is_public:
            button_html = 'Deleted'
        elif obj.is_removed:
            button_html = 'Hidden'
        else:
            button_html = 'Public'
        return format_html(button_html)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('flags')

    def num_replies(self, obj):
        return obj.nested_count

    def num_flags(self, obj):
        return obj.flags.count()

    def article(self, obj):
        return getattr(obj.content_object, 'title', 'N/A')

    def article_url(self, obj):
        return getattr(obj.content_object, 'url', 'N/A')

    def article_language_code(self, obj):
        locale = getattr(obj.content_object, 'locale', object)
        return getattr(locale, 'language_code', 'N/A')

    def view_live(self, obj):
        content_object = obj.content_object
        url = getattr(content_object, 'url', None)
        if url:
            return f'<a href="{url}" target="_blank">{content_object.title}</a>'

        return 'N/A'

    view_live.allow_tags = True

    @property
    def export_filename(self):
        return f'comments_{timezone.now().strftime(settings.EXPORT_FILENAME_TIMESTAMP_FORMAT)}'


class CannedResponseAdmin(ModelAdmin):
    model = CannedResponse
    menu_label = 'Canned Responses'
    menu_icon = 'placeholder'
    list_display = ('header', 'text')
    search_fields = ('header', 'text')
    menu_order = 602


class CommentsGroup(ModelAdminGroup):
    menu_label = 'Comments'
    menu_icon = 'openquote'
    menu_order = 600
    items = (XtdCommentAdmin, CannedResponseAdmin)


modeladmin_register(CommentsGroup)
