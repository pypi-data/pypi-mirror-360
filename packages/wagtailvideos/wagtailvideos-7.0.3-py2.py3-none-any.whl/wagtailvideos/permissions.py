from wagtail.permission_policies.collections import (
    CollectionOwnershipPermissionPolicy)

from wagtailvideos import get_video_model
from wagtailvideos.models import Video

permission_policy = CollectionOwnershipPermissionPolicy(
    get_video_model(),
    auth_model=Video,
    owner_field_name='uploaded_by_user'
)
