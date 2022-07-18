import locale
from django.urls import path, reverse
from django.utils.html import format_html_join
from django.templatetags.static import static
from wagtail.admin.menu import MenuItem

from wagtail.core import hooks
from wagtail.core.models import Locale

from questionnaires.views import FormPagesListView, UserSubmissionView


@hooks.register('insert_editor_js', order=100)
def editor_js():
    language_code = Locale.get_active().language_code
    js_files = [
        'js/blocks/skiplogic.js',
        'js/blocks/skiplogic_stream.js',
    ]
    js_includes = format_html_join('\n', '<script src="{0}"></script>',
        ((static(filename),) for filename in js_files)
    )
    js_includes = f'{js_includes}\n<script src="/{language_code}/jsi18n/"></script>'
    return js_includes


@hooks.register('register_admin_urls')
def register_custom_form_pages_list_view():
  return [
      path('forms/', FormPagesListView.as_view(), name='index'),
      path('user-submissions/', UserSubmissionView.as_view(), name='user_submissions'),
  ]


@hooks.register('register_admin_menu_item')
def register_calendar_menu_item():
    return MenuItem('User Submissions', reverse('user_submissions'), icon_name='date')
