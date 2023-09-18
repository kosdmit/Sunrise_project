import uuid

from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

from app_landing.models_mixins import CompressImageBeforeSaveMixin
from app_landing.validators import phone_number_validator

# Create your models here.
User = get_user_model()
class BaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4,
                            unique=True, verbose_name=_('unique identifier'))
    num_id = models.IntegerField(unique=True, editable=False, verbose_name=_('#'))

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   verbose_name=_('created by'), editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   verbose_name=_('updated by'), editable=False,
                                   related_name='+')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date of creation'))
    updated_date = models.DateTimeField(auto_now=True, verbose_name=_('date of updating'))

    is_active = models.BooleanField(default=False, verbose_name=_('is active'))

    class Meta:
        abstract = True

    def get_class_name(self):
        return self.__class__.__name__

    def save(self, *args, **kwargs):
        if not self.num_id:
            max_id = self.__class__.objects.all().aggregate(max_id=models.Max('num_id'))['max_id']
            if max_id is not None:
                self.num_id = max_id + 1
            else:
                self.num_id = 1
        super().save(*args, **kwargs)


class Project(BaseModel):
    title = models.CharField(max_length=150, verbose_name=_('title'))
    slug = AutoSlugField(populate_from='title', unique=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True,
                                 blank=True, verbose_name=_('category'))
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    is_featured = models.BooleanField(verbose_name=_('is featured project'), default=False)

    def save(self, *args, **kwargs):
        if self.is_featured:
            self.__class__.objects.filter(is_featured=True).update(is_featured=False)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return self.title


class Category(BaseModel):
    title = models.CharField(max_length=150, verbose_name=_('title'), unique=True)
    slug = AutoSlugField(populate_from='title', unique=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.title


class Parameter(BaseModel):
    project = models.ForeignKey('Project', verbose_name=_('project'), on_delete=models.CASCADE)

    title = models.CharField(max_length=150, verbose_name=_('title'))
    value = models.CharField(max_length=150, verbose_name=_('value'))

    class Meta:
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')

    def __str__(self):
        return self.title


class ProjectImage(CompressImageBeforeSaveMixin, BaseModel):
    def __init__(self, *args, **kwargs):
        self.image_width = 1920
        self.image_name_suffix = 'project_image'
        super().__init__(*args, **kwargs)

    project = models.ForeignKey('Project', on_delete=models.CASCADE,
                                related_name='images', verbose_name=_('project'))
    image = models.ImageField(upload_to='images/project_images/', verbose_name=_('image'))
    title = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('title'))
    description = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('description'))
    slug = AutoSlugField(populate_from='title', unique=True)
    ordering = models.IntegerField(default=0, verbose_name=_('ordering'))

    class Meta:
        verbose_name = _('project image')
        verbose_name_plural = _('project images')
        ordering = ['ordering', 'num_id']

    def __str__(self):
        if self.caption:
            return self.caption
        else:
            return super().__str__()


class Order(BaseModel):
    STATUSES = [
        ('new', _('new request')),
        ('active', _('in progress')),
        ('closed', _('closed')),
        ('production', _('in production')),
        ('success_sell', _('success sell')),
    ]

    DEFAULT_STATUS = STATUSES[0][0]

    customer_name = models.CharField(max_length=150, verbose_name=_('customer name'), null=True, blank=True)
    phone_number = models.CharField(max_length=20,
                                    validators=[phone_number_validator, ],
                                    verbose_name=_('phone number'),
                                    unique=True)
    status = models.CharField(max_length=12, choices=STATUSES, default=DEFAULT_STATUS, verbose_name=_('status'))
    note = models.TextField(null=True, blank=True, verbose_name=_('notes'))

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return (f"{gettext('order')} {gettext('#')} {str(self.num_id)} {gettext('from')} ") + \
               (f"{self.customer_name} ({self.phone_number})" if self.customer_name else self.phone_number)


class Tariff(BaseModel):
    title = models.CharField(max_length=150, verbose_name=_('title'))
    price = models.IntegerField(verbose_name=_('price'))
    price_prefix = models.BooleanField(default=False, verbose_name=_('price prefix'))
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    tariff_advantages = models.ManyToManyField('TariffAdvantage', verbose_name=_('tariff advantages'))
    is_featured = models.BooleanField(verbose_name=_('is featured tariff'), default=False)

    def save(self, *args, **kwargs):
        if self.is_featured:
            self.__class__.objects.filter(is_featured=True).update(is_featured=False)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('tariff')
        verbose_name_plural = _('tariffs')

    def __str__(self):
        return self.title


class TariffAdvantage(BaseModel):
    title = models.CharField(max_length=150, verbose_name=_('title'))
    ordering = models.IntegerField(default=0, verbose_name=_('ordering'))

    class Meta:
        verbose_name = _('tariff advantage')
        verbose_name_plural = _('tariff advantages')
        ordering = ['ordering', 'num_id']

    def __str__(self):
        return self.title
