import os
import uuid

from django.utils.text import slugify


def create_custom_path(instance, filename: str) -> str:
    root, extension = os.path.splitext(filename)
    return os.path.join(
        "uploads/images/",
        f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )
