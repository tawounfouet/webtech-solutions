import uuid
from django.utils.text import slugify

def generate_public_id(instance, *args, **kwargs):
    title = instance.title
    unique_id = str(uuid.uuid4()).replace("-", "")
    if not title:
        return unique_id
    slug = slugify(title)
    unique_id_short = unique_id[:5]
    return f"{slug}-{unique_id_short}"


def get_public_id_prefix(instance, *args, **kwargs):
    if hasattr(instance, 'path'):
        path = instance.path
        if path.startswith("/"):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        return path
    public_id = instance.public_id
    model_class = instance.__class__
    model_name = model_class.__name__
    model_name_slug = slugify(model_name)
    if not public_id:
        return f"{model_name_slug}"
    return f"{model_name_slug}/{public_id}"

# def get_display_name(instance, *args, **kwargs):
#     if hasattr(instance, 'get_display_name'):
#         return instance.get_display_name()
#     elif hasattr(instance, 'title'):
#         return instance.title
#     model_class = instance.__class__
#     model_name = model_class.__name__
#     return f"{model_name} Upload"


def get_display_name(instance, *args, **kwargs):
    if hasattr(instance, 'get_display_name'):
        return instance.get_display_name()
    elif hasattr(instance, 'title'):
        return instance.title
    elif hasattr(instance, 'name'):  # Assuming 'name' holds the desired image name
        return instance.name
    elif hasattr(instance, 'slug'):  # Assuming 'name' holds the desired image slug
        return instance.slug
    model_class = instance.__class__
    model_name = model_class.__name__
    return f"{model_name} Upload"

