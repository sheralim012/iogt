from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (FieldPanel,
                                         InlinePanel, MultiFieldPanel,
                                         ObjectList, PageChooserPanel,
                                         StreamFieldPanel, TabbedInterface)
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page

from wagtail.core.rich_text import get_text_for_indexing
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtailmarkdown.blocks import MarkdownBlock

from comments.models import CommentableMixin
from iogt.views import create_final_external_link

from .blocks import (MediaBlock, SocialMediaLinkBlock,
                     SocialMediaShareButtonBlock)


class HomePage(Page):
    template = 'home/home_page.html'

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            InlinePanel('home_page_banners', label=_("Home Page Banner")),
        ], heading=_('Home Page Banners')),
        MultiFieldPanel([
            InlinePanel('featured_content', label=_("Featured Content")),
        ], heading=_('Featured Content')),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['banners'] = [
            home_page_banner.banner_page for home_page_banner in self.home_page_banners.filter(banner_page__live=True)
        ]
        context['featured_content'] = [
            featured_content.content for featured_content in self.featured_content.filter(content__live=True)
        ]
        return context


class FeaturedContent(Orderable):
    source = ParentalKey(Page, related_name='featured_content', on_delete=models.CASCADE, blank=True)
    content = models.ForeignKey(Page, on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('content'),
    ]


class HomePageBanner(Orderable):
    source = ParentalKey(Page, related_name='home_page_banners', on_delete=models.CASCADE, blank=True)
    banner_page = models.ForeignKey('home.BannerPage', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('banner_page'),
    ]


class Section(Page):
    icon = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )
    icon_active = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )
    color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
    )
    show_in_menus_default = True

    content_panels = Page.content_panels + [
        ImageChooserPanel('icon'),
        ImageChooserPanel('icon_active'),
        FieldPanel('color'),
        MultiFieldPanel([
            InlinePanel('featured_content', max_num=1, label=_("Featured Content")),
        ], heading=_('Featured Content')),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['featured_content'] = [
            featured_content.content for featured_content in self.featured_content.filter(content__live=True)
        ]
        context['sub_sections'] = self.get_children().live().type(Section)
        context['articles'] = self.get_children().live().type(Article)
        return context


class ArticleTag(TaggedItemBase):
    """The through model between Article and Tag"""
    content_object = ParentalKey('Article', related_name='tagged_items', on_delete=models.CASCADE)


class ArticleRecommendation(Orderable):
    source = ParentalKey('Article', related_name='recommended_articles', on_delete=models.CASCADE, blank=True)
    article = models.ForeignKey('Article', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('article')
    ]


class SectionRecommendation(Orderable):
    source = ParentalKey('Article', related_name='recommended_sections', on_delete=models.CASCADE)
    section = models.ForeignKey('Section', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('section')
    ]


class Article(Page, CommentableMixin):
    lead_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )

    tags = ClusterTaggableManager(through=ArticleTag, blank=True)
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('markdown', MarkdownBlock(icon='code')),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('numbered_list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('page', blocks.PageChooserBlock()),
        ('media', MediaBlock(icon='media')),
    ])
    show_in_menus_default = True

    def _get_child_block_values(self, block_type):
        searchable_content = []
        for block in self.body:
            if block.block_type == block_type:
                value = force_str(block.value)
                searchable_content.append(get_text_for_indexing(value))
        return searchable_content

    def get_heading_values(self):
        heading_values = self._get_child_block_values('heading')
        return '\n'.join(heading_values)

    def get_paragraph_values(self):
        paragraph_values = self._get_child_block_values('paragraph')
        return '\n'.join(paragraph_values)

    content_panels = Page.content_panels + [
        ImageChooserPanel('lead_image'),
        StreamFieldPanel('body'),
        MultiFieldPanel([
            InlinePanel('recommended_articles', label=_("Recommended Articles")),
            InlinePanel('recommended_sections', label=_("Recommended Sections"))
        ],
            heading='Recommended Content')
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([FieldPanel("tags"), ], heading='Metadata'),
    ]

    search_fields = [
        index.SearchField('get_heading_values', partial_match=True, boost=1),
        index.SearchField('get_paragraph_values', partial_match=True),
        index.SearchField('title', partial_match=True, boost=2),

        index.FilterField('live')
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings'),
        ObjectList(CommentableMixin.comments_panels, heading='Comments')
    ])

    def get_context(self, request):
        context = super().get_context(request)
        context['breadcrumbs'] = [crumb for crumb in self.get_ancestors() if not crumb.is_root()]
        context['sections'] = self.get_ancestors().type(Section)
        return context

    def description(self):
        for block in self.body:
            if block.block_type == 'paragraph':
                return block
        return ''


class BannerIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.BannerPage']


class BannerPage(Page):
    parent_page_types = ['home.BannerIndexPage']
    subpage_types = []

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        on_delete=models.PROTECT,
        help_text=_('Image to display as the banner')
    )
    banner_link_page = models.ForeignKey(
        Page, null=True, blank=True, related_name='banners', on_delete=models.PROTECT,
        help_text=_('Optional page to which the banner will link to'))
    external_link = models.URLField(
        null=True, blank=True,
        help_text=_('Optional external link which a banner will link to e.g., https://www.google.com'))

    content_panels = Page.content_panels + [
        ImageChooserPanel('banner_image'),
        PageChooserPanel('banner_link_page'),
        FieldPanel('external_link'),
    ]

    @property
    def final_external_link(self):
        if self.banner_link_page:
            return self.banner_link_page.url
        if self.external_link:
            return create_final_external_link(self.external_link)
        else:
            return "#"


class FooterIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.FooterPage']

    def __str__(self):
        return self.title


class FooterPage(Article):
    parent_page_types = ['home.FooterIndexPage']
    subpage_types = []
    template = 'home/article.html'


@register_setting
class SiteSettings(BaseSetting):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    show_only_translated_pages = models.BooleanField(
        default=False,
        help_text='When selecting this option, untranslated pages'
                  ' will not be visible to the front end user'
                  ' when viewing a child language of the site')
    # TODO: GA, FB analytics should be global.
    fb_analytics_app_id = models.CharField(
        verbose_name=_('Facebook Analytics App ID'),
        max_length=25,
        null=True,
        blank=True,
        help_text=_(
            "The tracking ID to be used to view Facebook Analytics")
    )
    local_ga_tag_manager = models.CharField(
        verbose_name=_('Local GA Tag Manager'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Local GA Tag Manager tracking code (e.g GTM-XXX) to be used to "
            "view analytics on this site only")
    )
    global_ga_tag_manager = models.CharField(
        verbose_name=_('Global GA Tag Manager'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Global GA Tag Manager tracking code (e.g GTM-XXX) to be used"
            " to view analytics on more than one site globally")
    )
    local_ga_tracking_code = models.CharField(
        verbose_name=_('Local GA Tracking Code'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Local GA tracking code to be used to "
            "view analytics on this site only")
    )
    global_ga_tracking_code = models.CharField(
        verbose_name=_('Global GA Tracking Code'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Global GA tracking code to be used"
            " to view analytics on more than one site globally")
    )
    social_media_link = StreamField([
        ('social_media_link', SocialMediaLinkBlock()),
    ], null=True, blank=True)
    social_media_content_sharing_button = StreamField([
        ('social_media_content_sharing_button', SocialMediaShareButtonBlock()),
    ], null=True, blank=True)
    media_file_size_threshold = models.IntegerField(
        default=9437184,
        help_text='Show warning if uploaded media file size is greater than this in bytes. Default is 9 MB')
    allow_anonymous_comment = models.BooleanField(default=False)

    panels = [
        ImageChooserPanel('logo'),
        MultiFieldPanel(
            [
                FieldPanel('show_only_translated_pages'),
            ],
            heading="Multi Language",
        ),
        MultiFieldPanel(
            [
                FieldPanel('fb_analytics_app_id'),
            ],
            heading="Facebook Analytics Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel('local_ga_tag_manager'),
                FieldPanel('global_ga_tag_manager'),
            ],
            heading="GA Tag Manager Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel('local_ga_tracking_code'),
                FieldPanel('global_ga_tracking_code'),
            ],
            heading="GA Tracking Code Settings",
        ),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        StreamFieldPanel('social_media_link'),
                    ],
                    heading="Social Media Footer Page", ),
            ],
            heading="Social Media Page Links", ),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        StreamFieldPanel('social_media_content_sharing_button'),
                    ],
                    heading="Social Media Content Sharing Buttons", ),
            ],
            heading="Social Media Content Sharing Buttons", ),
        MultiFieldPanel(
            [
                FieldPanel('media_file_size_threshold'),
            ],
            heading="Media File Size Threshold",
        ),
        MultiFieldPanel(
            [
                FieldPanel('allow_anonymous_comment'),
            ],
            heading="Allow Anonymous Comment",
        ),
    ]

    def __str__(self):
        return self.site.site_name

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
