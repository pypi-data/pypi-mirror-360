from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import CustomVideoModel
from wagtailvideos import get_video_model, get_video_model_string
from wagtailvideos.models import Video


class TestGetVideoModel(WagtailTestUtils, TestCase):
    @override_settings(WAGTAILVIDEOS_VIDEO_MODEL='app.CustomVideoModel')
    def test_custom_get_video_model(self):
        self.assertIs(get_video_model(), CustomVideoModel)

    @override_settings(WAGTAILVIDEOS_VIDEO_MODEL='app.CustomVideoModel')
    def test_custom_get_video_model_string(self):
        self.assertEqual(get_video_model_string(), 'app.CustomVideoModel')

    def test_standard_get_video_model(self):
        self.assertIs(get_video_model(), Video)

    def test_standard_get_video_model_string(self):
        self.assertEqual(get_video_model_string(), 'wagtailvideos.Video')

    @override_settings(WAGTAILVIDEOS_VIDEO_MODEL='app.UnknownModel')
    def test_unknown_get_video_model(self):
        with self.assertRaises(ImproperlyConfigured):
            get_video_model()

    @override_settings(WAGTAILVIDEOS_VIDEO_MODEL='invalid-string')
    def test_invalid_get_video_model(self):
        with self.assertRaises(ImproperlyConfigured):
            get_video_model()
