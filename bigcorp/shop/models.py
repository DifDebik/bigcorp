import random
import string

from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.text import slugify


def random_slug():
    """
    Generates a random slug consisting of 3 alphanumeric characters.
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))


class Category(models.Model):
    name = models.CharField('Категория', max_length=255, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    slug = models.SlugField('URL', max_length=255, unique=True, null=False, editable=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        unique_together = (['slug', 'parent'])
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        """
        Return a string representation of the full path, including the parent names.
        """
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def save(self, *args, **kwargs):
        """
        Save the object with the given arguments and keyword arguments.
        """
        if not self.slug:
            self.slug = slugify(random_slug() + '-pickBetter' + self.name) 
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("model_detail", kwargs={"pk": self.pk})



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField('Название', max_length=255)
    brand = models.CharField('Бренд', max_length=255)
    description = models.TextField('Описание', blank=True)
    slug = models.SlugField('URL', max_length=255)
    price = models.DecimalField('Цена', max_digits=7, decimal_places=2, default=99.99)
    image = models.ImageField('Изображение', upload_to='products/products/%Y/%m/%d')
    available = models.BooleanField('Наличие', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self) -> str:
        """
        Return a string representation of the object.
        """
        return self.title
    
    def get_absolute_url(self):
        return reverse("model_detail", kwargs={"pk": self.pk})
    



class ProductManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        """
        Return a queryset filtered by availability.
        """
        return super(ProductManager, self).get_queryset().filter(available=True)

class ProductProxy(Product):
    objects = ProductManager()

    class Meta:
        proxy = True
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'