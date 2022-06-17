import os
from pathlib import Path

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.admin.utils import flatten
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import translation
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.core.models import Page, Locale
from wagtail.images.models import Rendition
from wagtailmedia.models import Media

from questionnaires.models import Poll, Survey, Quiz


def check_user_session(request):
    if request.method == "POST":
        request.session["first_time_user"] = False


def create_final_external_link(next_page):
    transition_page = reverse("external-link")
    return f"{transition_page}?next={next_page}"


class TransitionPageView(TemplateView):
    template_name = "transition-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["next"] = self.request.GET.get("next", "/")
        context["prev"] = self.request.META.get("HTTP_REFERER", "/")
        return context


class TranslationNotFoundPage(TemplateView):
    template_name = "translation_not_found_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        from home.models import HomePage
        origin_page = get_object_or_404(Page, pk=self.request.GET.get('page'))

        context['home_page'] = HomePage.objects.first().localized
        context['prev'] = origin_page.url

        context['page_title'] = origin_page.title
        return context


class SitemapAPIView(APIView):
    def get(self, request):
        from home.models import HomePage, Section, Article, FooterPage, OfflineAppPage, SVGToPNGMap

        home_page_urls = [p.url for p in HomePage.objects.live()],
        section_urls = [p.url for p in Section.objects.live()],
        article_urls = [p.url for p in Article.objects.live()],
        footer_urls = [p.url for p in FooterPage.objects.live()],
        poll_urls = [p.url for p in Poll.objects.live()],
        survey_urls = [p.url for p in Survey.objects.live()],
        quiz_urls = [p.url for p in Quiz.objects.live()],
        offline_app_page_urls = [p.url for p in OfflineAppPage.objects.live()],

        jsi18n_urls = []
        for locale in Locale.objects.all():
            jsi18n_urls.append(f'/{locale.language_code}/jsi18n/')

        image_urls = []
        for image in Rendition.objects.all():
            image_urls.append(f'{settings.MEDIA_URL}{image.file.name}')

        for image in SVGToPNGMap.objects.all():
            image_urls.append(f'{settings.MEDIA_URL}{image.png_image_file.name}')

        media_urls = []
        for media in Media.objects.all():
            media_urls.append(f'{settings.MEDIA_URL}{media.file.name}')
            if media.thumbnail:
                image_urls.append(f'{settings.MEDIA_URL}{media.thumbnail.name}')

        static_urls = []
        static_dirs = [
            {'name': 'css', 'extensions': ('.css',)},
            {'name': 'js', 'extensions': ('.js',)},
            {'name': 'fonts', 'extensions': ('.woff', '.woff2',)},
            {'name': 'icons', 'extensions': ('.svg',)},
        ]
        for static_dir in static_dirs:
            for root, dirs, files in os.walk(Path(settings.STATIC_ROOT) / static_dir['name']):
                for file in files:
                    if file.endswith(static_dir['extensions']):
                        static_urls.append(f'{settings.STATIC_URL}{root.split("/static/")[-1]}/{file}')

        sitemap = flatten(
            home_page_urls +
            section_urls +
            article_urls +
            footer_urls +
            poll_urls +
            survey_urls +
            quiz_urls +
            offline_app_page_urls +
            tuple(static_urls) +
            tuple(image_urls) +
            tuple(media_urls) +
            tuple(jsi18n_urls)
        )
        return Response(sitemap)


class PageTreeAPIView(APIView):
    def _get_renditions(self, image_id):
        image_urls = []
        for rendition in Rendition.objects.filter(image_id=image_id):
            image_urls.append(f'{settings.MEDIA_URL}{rendition.file.name}')
        return image_urls

    def _get_banner_image_urls(self, page):
        image_urls = []
        if page.banner_image:
            image_urls += self._get_renditions(page.banner_image)
        return image_urls

    def _get_lead_image_urls(self, page):
        image_urls = []
        if page.lead_image:
            image_urls += self._get_renditions(page.lead_image)
        return image_urls

    def _get_image_icon_urls(self, page):
        image_urls = []
        if page.image_icon:
            image_urls += self._get_renditions(page.image_icon)
        return image_urls

    def _get_stream_data_image_urls(self, stream_data):
        image_urls = []
        for block in stream_data:
            if block['type'] == 'image':
                image_urls += self._get_renditions(block['value'])
            if block['type'] == 'paragraph':
                tags = BeautifulSoup(block['value'], "html.parser").find_all('embed')
                for tag in tags:
                    if tag.attrs['embedtype'] == 'image':
                        image_urls += self._get_renditions(tag.attrs['id'])
        return image_urls

    def _get_page_image_urls(self, page):
        from home.models import BannerPage, Section, Article, OfflineAppPage

        image_urls = []
        if isinstance(page, (BannerPage,)):
            image_urls += self._get_banner_image_urls(page)
        if isinstance(page, (Section, Article, OfflineAppPage)):
            image_urls += self._get_lead_image_urls(page)
        if isinstance(page, (Section, Article, OfflineAppPage, Poll, Survey, Quiz)):
            image_urls += self._get_image_icon_urls(page)
        if isinstance(page, (Article, OfflineAppPage)):
            image_urls += self._get_stream_data_image_urls(page.body.stream_data)
        if isinstance(page, (Poll, Survey, Quiz)):
            image_urls += self._get_stream_data_image_urls(page.description.stream_data)
            image_urls += self._get_stream_data_image_urls(page.thank_you_text.stream_data)
        return image_urls

    def get(self, request, page_id):
        from home.models import HomePage, Section, Article, OfflineAppPage, SVGToPNGMap
        page = get_object_or_404(Page, id=page_id)
        pages = page.get_descendants(inclusive=True).live().specific()
        page_urls = []
        image_urls = []
        for page in pages:
            if isinstance(page, (HomePage, Section, Article, OfflineAppPage, Poll, Survey, Quiz)):
                page_urls.append(page.url)
                image_urls += self._get_page_image_urls(page)

        for svg_to_png_map in SVGToPNGMap.objects.all():
            image_urls.append(f'{settings.MEDIA_URL}{svg_to_png_map.png_image_file.name}')

        language = translation.get_language()
        jsi18n_urls = [
            f'/{language}/jsi18n/'
        ]

        static_urls = []
        static_dirs = [
            {'name': 'css', 'extensions': ('.css',)},
            {'name': 'js', 'extensions': ('.js',)},
            {'name': 'fonts', 'extensions': ('.woff', '.woff2',)},
            {'name': 'icons', 'extensions': ('.svg',)},
        ]
        for static_dir in static_dirs:
            for root, dirs, files in os.walk(Path(settings.STATIC_ROOT) / static_dir['name']):
                for file in files:
                    if file.endswith(static_dir['extensions']):
                        static_urls.append(f'{settings.STATIC_URL}{root.split("/static/")[-1]}/{file}')


        urls = set(flatten(
            page_urls +
            image_urls +
            jsi18n_urls +
            static_urls
        ))
        return Response(urls)
