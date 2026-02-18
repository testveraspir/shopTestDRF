from django.core.exceptions import ValidationError


def validate_image_size(image):
    """Проверяет, что размер изображения не превышает 5MB"""
    max_size = 5 * 1024 * 1024

    if image.size > max_size:
        size_mb = image.size / (1024 * 1024)
        raise ValidationError(
            f"Размер файла {size_mb:.1f}MB превышает максимальный 5MB"
        )
