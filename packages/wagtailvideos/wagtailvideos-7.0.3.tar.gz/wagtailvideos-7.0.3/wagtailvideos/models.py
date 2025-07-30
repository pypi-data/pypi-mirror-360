import logging
import mimetypes
import os
import os.path

import bcp47
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.db import models
from django.forms.utils import flatatt
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from wagtail.admin.models import get_object_usage
from wagtail.models import CollectionMember, Orderable
from wagtail.search import index
from wagtail.search.queryset import SearchableQuerySetMixin

from . import get_transcoder_backend
from .enums import MediaFormats, VideoQuality, VideoTrackKind

logger = logging.getLogger(__name__)


def _choices(text_choices, max_length=None):
    """Return a kwargs dict for adding choices and max_length to a CharField"""
    if max_length is None:
        max_length = max([len(choice) for choice in text_choices.values])
    return {
        "choices": text_choices.choices,
        "max_length": max_length,
    }


class VideoQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


def get_upload_to(instance, filename):
    # Dumb proxy to instance method.
    return instance.get_upload_to(filename)


class AbstractVideo(CollectionMember, index.Indexed, models.Model):
    title = models.CharField(max_length=255, verbose_name=_('title'))
    file = models.FileField(
        verbose_name=_('file'), upload_to=get_upload_to)
    thumbnail = models.ImageField(upload_to=get_upload_to, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True, db_index=True)
    duration = models.DurationField(blank=True, null=True)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('uploaded by user'),
        null=True, blank=True, editable=False, on_delete=models.SET_NULL
    )

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_('tags'))

    file_size = models.PositiveIntegerField(null=True, editable=False)
    width = models.IntegerField(verbose_name=_("width"), editable=False, null=True)
    height = models.IntegerField(verbose_name=_("height"), editable=False, null=True)

    objects = VideoQuerySet.as_manager()

    search_fields = list(CollectionMember.search_fields) + [
        index.AutocompleteField('title', boost=10),
        index.RelatedFields('tags', [
            index.AutocompleteField('name', boost=10),
        ]),
        index.FilterField('uploaded_by_user'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_file = self.file

    def get_file_size(self):
        if self.file_size is None:
            try:
                self.file_size = self.file.size
            except OSError:
                # File doesn't exist
                return

            self.save(update_fields=['file_size'])

        return self.file_size

    def get_upload_to(self, filename):
        folder_name = 'original_videos'
        filename = self.file.field.storage.get_valid_name(filename)
        max_length = self._meta.get_field('file').max_length

        # Truncate filename so it fits in the 100 character limit
        # https://code.djangoproject.com/ticket/9893
        file_path = os.path.join(folder_name, filename)
        too_long = len(file_path) - max_length
        if too_long > 0:
            head, ext = os.path.splitext(filename)
            if too_long > len(head) + 1:
                raise SuspiciousFileOperation('File name can not be shortened to a safe length')
            filename = head[:-too_long] + ext
        return os.path.join(folder_name, filename)

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse('wagtailvideos:video_usage', args=(self.id,))

    @property
    def formatted_duration(self):
        if self.duration:
            hours, remainder = divmod(self.duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return "%d:%02d:%02d" % (hours, minutes, seconds)
        return ''

    def __str__(self):
        return self.title

    @property
    def url(self):
        return self.file.url

    def filename(self, include_ext=True):
        if include_ext:
            return os.path.basename(self.file.name)
        else:
            return os.path.splitext(os.path.basename(self.file.name))[0]

    @property
    def file_ext(self):
        return os.path.splitext(self.filename())[1][1:]

    @property
    def content_type(self):
        mime = mimetypes.MimeTypes()
        return mime.guess_type(self.url)[0] or mime.guess_type(self.filename())[0]

    def is_editable_by_user(self, user):
        from wagtailvideos.permissions import permission_policy
        return permission_policy.user_has_permission_for_instance(user, 'change', self)

    @classmethod
    def get_transcode_model(cls):
        return cls.transcodes.rel.related_model

    @classmethod
    def get_track_listing_model(cls):
        return cls.track_listing.related.related_model

    def get_current_transcodes(self):
        return self.transcodes.exclude(processing=True).filter(error_message__exact='')

    def get_tracks(self):
        tracks = []
        if hasattr(self, 'track_listing'):
            tracks = [t.track_tag() for t in self.track_listing.tracks.all()]
        return tracks

    def video_tag(self, attrs=None):
        if attrs is None:
            attrs = {}
        else:
            attrs = attrs.copy()
        if self.thumbnail:
            attrs['poster'] = self.thumbnail.url

        transcodes = self.get_current_transcodes()
        sources = []
        for transcode in transcodes:
            sources.append("<source src='{0}' type='video/{1}' >".format(transcode.url, transcode.media_format))

        sources.append("<source src='{0}' type='{1}'>"
                       .format(self.url, self.content_type))

        sources.append("<p>Sorry, your browser doesn't support playback for this video</p>")

        return mark_safe(
            "<video {0}>\n{1}\n{2}\n</video>".format(flatatt(attrs), "\n".join(sources), "\n".join(self.get_tracks())))

    def do_transcode(self, media_format, quality):
        transcode, created = self.transcodes.get_or_create(
            media_format=media_format,
        )
        if created or transcode.processing is False:
            transcode.processing = True
            transcode.error_messages = ''
            transcode.quality = quality
            # Lock the transcode model
            transcode.save(update_fields=['processing', 'error_message',
                                          'quality'])
            # Generate the transcode using the selected transcoding backend
            backend = get_transcoder_backend()
            backend.do_transcode(transcode)
        else:
            pass  # TODO Queue?

    class Meta:
        abstract = True


class Video(AbstractVideo):
    admin_form_fields = (
        'title',
        'file',
        'collection',
        'thumbnail',
        'tags',
    )

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("choose_video", "Can choose video"),
        ]


class AbstractVideoTranscode(models.Model):
    media_format = models.CharField(**_choices(MediaFormats))
    quality = models.CharField(**_choices(VideoQuality), default=VideoQuality.DEFAULT)
    processing = models.BooleanField(default=False)
    file = models.FileField(null=True, blank=True, verbose_name=_('file'),
                            upload_to=get_upload_to)
    error_message = models.TextField(blank=True)

    @property
    def url(self):
        if self.file:
            return self.file.url
        return ''

    def get_upload_to(self, filename):
        folder_name = 'video_transcodes'
        filename = self.file.field.storage.get_valid_name(filename)
        return os.path.join(folder_name, filename)

    class Meta:
        abstract = True


class VideoTranscode(AbstractVideoTranscode):
    video = models.ForeignKey(Video, related_name='transcodes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('video', 'media_format')


class AbstractTrackListing(ClusterableModel):
    def __str__(self):
        return self.video.title

    @classmethod
    def get_track_model(cls):
        return cls.tracks.rel.related_model

    class Meta:
        abstract = True


class TrackListing(AbstractTrackListing):
    video = models.OneToOneField(
        Video, on_delete=models.CASCADE,
        related_name='track_listing')


class AbstractVideoTrack(Orderable):
    file = models.FileField(
        verbose_name=_('File'),
        upload_to=get_upload_to
    )
    kind = models.CharField(**_choices(VideoTrackKind, max_length=50), default=VideoTrackKind.SUBTITLES, verbose_name=_('Kind'))
    label = models.CharField(
        max_length=255, blank=True,
        help_text=_('A user-readable title of the text track.'),
        verbose_name=_('Label'))
    language = models.CharField(
        max_length=50,
        choices=[(v, k) for k, v in bcp47.languages.items()],
        default='en', blank=True, help_text=_('Required if type is "Subtitle"'),
        verbose_name=_('Language'))

    def track_tag(self):
        attrs = {
            'kind': self.kind,
            'src': self.url,
        }
        if self.label:
            attrs['label'] = self.label
        if self.language:
            attrs['srclang'] = self.language

        return "<track {0}{1}>".format(flatatt(attrs), ' default' if self.sort_order == 0 else '')

    def __str__(self):
        return "{0} - {1}".format(self.label or self.get_kind_display(), self.get_language_display())

    @property
    def url(self):
        return self.file.url

    def get_upload_to(self, filename):
        folder_name = 'video_tracks'
        filename = self.file.field.storage.get_valid_name(filename)
        return os.path.join(folder_name, filename)

    class Meta:
        abstract = True


class VideoTrack(AbstractVideoTrack):
    listing = ParentalKey(TrackListing, related_name='tracks', on_delete=models.CASCADE)
