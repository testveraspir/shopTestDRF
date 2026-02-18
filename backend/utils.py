from django.utils.text import slugify
from unidecode import unidecode


def generate_unique_slug(
        instance,
        field_name='name',
        slug_field_name='slug'):
    """
    Генерирует уникальный slug для модели
    """

    if instance.pk is None:
        value = str(getattr(instance, field_name))
        slug = slugify(unidecode(value))
        if not slug:
            slug = f'default-{instance.pk}'
        original_slug = slug
        counter = 1
        model_class = instance.__class__
        while model_class.objects.filter(**{slug_field_name: slug}
                                         ).exists():
            slug = f'{original_slug}-{counter}'
            counter += 1
        setattr(instance, slug_field_name, slug)
