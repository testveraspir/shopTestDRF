from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from .validators import validate_image_size


class Category(models.Model):
    """Модель категорий"""

    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='URL-идентификатор',
        blank=True
    )
    image = models.ImageField(
        upload_to='categories/',
        verbose_name='Изображение',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text='Максимальный размер: 5МВ'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Категории"
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # автоматическое создание slug из названия
        if not self.slug:
            self.slug = slugify(self.name)
        original_slug = self.slug
        counter = 1
        while Category.objects.filter(slug=self.slug).exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
        super().save(*args, **kwargs)


class Subcategory(models.Model):
    """Модель подкатегорий"""

    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='Категория'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='URL-идентификатор',
        blank=True
    )
    image = models.ImageField(
        upload_to='subcategories/',
        verbose_name='Изображение',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text='Максимальный размер: 5МВ'
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = "Подкатегории"
        ordering = ('category', 'name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # автоматическое создание slug из названия
        if not self.slug:
            self.slug = slugify(self.name)
        original_slug = self.slug
        counter = 1
        while Subcategory.objects.filter(slug=self.slug).exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Модель продукта, которая содержит основную информацию
    о продукте и связь с категорией и подкатегорией.
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Название продукта'
    )
    category = models.ForeignKey(
        Category, verbose_name='Категория',
        related_name='products',
        blank=True,
        on_delete=models.CASCADE)
    subcategory = models.ForeignKey(
        Subcategory,
        verbose_name='Подкатегория',
        related_name='products',
        blank=True,
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='URL-идентификатор',
        blank=True
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Изображение',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text='Максимальный размер: 5МВ'
    )
    image_small = ImageSpecField(
        source='image',
        processors=[ResizeToFill(100, 100)],
        format='JPEG',
        options={'quality': 85}
    )
    image_medium = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 90}
    )
    image_large = ImageSpecField(
        source='image',
        processors=[ResizeToFill(800, 800)],
        format='JPEG',
        options={'quality': 95}
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # автоматическое создание slug из названия
        if not self.slug:
            self.slug = slugify(self.name)
        original_slug = self.slug
        counter = 1
        while Product.objects.filter(slug=self.slug).exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Модель корзины пользователя."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-created_at']


class CartItem(models.Model):
    """
    Модель позиции в корзине, связывает заказ
    с конкретным продуктом и его количеством.
    """

    cart = models.ForeignKey(
        Cart,
        verbose_name='Корзина',
        on_delete=models.CASCADE,
        related_name='cart_items',
        blank=True,
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Информация о продукте',
        related_name='cart_items',
        blank=True,
        on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1)

    class Meta:
        verbose_name = 'Выбранная позиция'
        verbose_name_plural = "Список выбранных позиций"
        unique_together = ['cart', 'product']

    def __str__(self):
        return f'{self.product.name} X {self.quantity}'

    @property
    def total_price(self):
        return self.product.price * self.quantity
