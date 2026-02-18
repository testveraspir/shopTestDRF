from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Subcategory, Product


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    fields = ['name', 'slug', 'image_preview']
    readonly_fields = ['slug', 'image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = 'Изображение'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'image_preview']
    readonly_fields = ['slug']
    inlines = [SubcategoryInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug')
        }),

    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = 'Изображение'


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'image_preview']
    list_filter = ['category']
    readonly_fields = ['slug']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "—"

    image_preview.short_description = 'Изображение'


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['category', 'subcategory']:
            if field_name in self.fields:
                field = self.fields[field_name]
                field.widget.can_add_related = False
                field.widget.can_change_related = False
                field.widget.can_delete_related = False
                field.widget.can_view_related = False
                field.empty_label = None
                field.required = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'category', 'subcategory', 'price', 'slug', 'image_preview']
    list_filter = ['category', 'subcategory']
    search_fields = ['name']
    readonly_fields = ['slug', 'image_preview']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'price')
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview'),
            'description': 'Максимальный размер: 5МВ'
        }),
        ('Категория', {
            'fields': ('category', 'subcategory')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "—"

    image_preview.short_description = 'Изображение'
