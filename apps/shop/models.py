from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


def generate_unique_slug(instance, name_field):
    name_val = getattr(instance, name_field)
    base_slug = slugify(unidecode(name_val))
    slug = base_slug
    num = 1
    model_class = instance.__class__
    
    while model_class.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{num}"
        num += 1
    return slug


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название товара")
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    category = models.ForeignKey(
        'Category',
        related_name='products',
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    tags = models.ManyToManyField("Tag", related_name='products', blank=True, verbose_name='Теги')
    manufacturer = models.ForeignKey(
        'Manufacturer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="Производитель"
    )
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.IntegerField(default=0, verbose_name="Остаток на складе")
    is_active = models.BooleanField(default=True, verbose_name="Доступен для продажи")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Владелец товара"
    )
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    viewed_by_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='viewed_products',
        blank=True,
        verbose_name="Просмотрено пользователями"
    )


    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'product_slug': self.slug})


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, 'name')
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, editable=False)


    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = "категории"


    def get_absolute_url(self):
        return reverse('shop:category_products', kwargs={'category_slug': self.slug})


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, editable=False)


    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"


    def get_absolute_url(self):
        return reverse('shop:tag_products', kwargs={'tag_slug': self.slug})


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


    def __str__(self):
        return f'#{self.name}'


class Manufacturer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, editable=False, verbose_name="URL-слаг")
    country = models.CharField(max_length=100, verbose_name="Страна")
    website = models.URLField(blank=True, null=True, verbose_name="Сайт")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def get_absolute_url(self):
        return reverse('shop:manufacturer_products', kwargs={'manufacturer_slug': self.slug})

    def __str__(self):
        return self.name