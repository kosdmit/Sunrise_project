import uuid

from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

from app_landing.models_mixins import CompressImageBeforeSaveMixin
from app_landing.validators import phone_number_validator

# Create your models here.
User = get_user_model()


class BaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False,
                            default=uuid.uuid4,
                            unique=True, verbose_name=_('unique identifier'))
    num_id = models.IntegerField(unique=True, editable=False, verbose_name=_('#'))

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   verbose_name=_('created by'), editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   verbose_name=_('updated by'), editable=False,
                                   related_name='+')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date of creation'))
    updated_date = models.DateTimeField(auto_now=True, verbose_name=_('date of updating'))

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active'),
        help_text=_("If this option is disabled, the object will be unavailable to users"),
    )

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
    title = models.CharField(
        max_length=24,
        verbose_name=_('title'),
        help_text=_("The maximum length is ") + "24" + _(" characters"),
    )
    slug = AutoSlugField(populate_from='title', unique=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True,
                                 blank=True, verbose_name=_('category'))
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    is_featured = models.BooleanField(
        verbose_name=_('is featured project'),
        default=False,
        help_text=_("If the option is active the project will have a special display on the site taking up large spaces"),
    )
    to_show_download_date = models.BooleanField(
        verbose_name=_('to show download date'),
        default=True,
        help_text=_("If the option is active, the user will see the project update date"),
    )

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return self.title


class Category(BaseModel):
    title = models.CharField(
        max_length=24,
        verbose_name=_('title'),
        unique=True,
        help_text=_("The maximum length is ") + "24" + _(" characters"),
    )
    slug = AutoSlugField(populate_from='title', unique=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.title


class Parameter(BaseModel):
    project = models.ForeignKey('Project', verbose_name=_('project'), on_delete=models.CASCADE)

    title = models.CharField(
        max_length=25,
        verbose_name=_('title'),
        help_text=_("The maximum length is ") + "25" + _(" characters"),
    )
    value = models.CharField(
        max_length=40,
        verbose_name=_('value'),
        help_text=_("The maximum length is ") + "40" + _(" characters"),
    )

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
    title = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        verbose_name=_('title'),
        help_text=_("The maximum length is ") + "45" + _(" characters") +
                  _(". This text will be displayed only on desktop screens"),
    )
    description = models.CharField(
        max_length=110,
        null=True,
        blank=True,
        verbose_name=_('description'),
        help_text=_("The maximum length is ") + "110" + _(" characters") +
                  _(". This text will be displayed only on desktop screens"),
    )
    slug = AutoSlugField(populate_from='title', unique=True)
    ordering = models.IntegerField(
        default=0,
        verbose_name=_('ordering'),
        help_text=_("This parameter is used in ascending order to sort objects"),
    )

    class Meta:
        verbose_name = _('project image')
        verbose_name_plural = _('project images')
        ordering = ['ordering', 'num_id']

    def __str__(self):
        if self.title:
            return self.title
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

    customer_name = models.CharField(max_length=150,
                                     verbose_name=_('customer name'),
                                     null=True, blank=True)
    phone_number = models.CharField(max_length=20,
                                    validators=[phone_number_validator, ],
                                    verbose_name=_('phone number'),
                                    unique=True)
    status = models.CharField(max_length=12, choices=STATUSES,
                              default=DEFAULT_STATUS, verbose_name=_('status'))
    note = models.TextField(null=True, blank=True, verbose_name=_('notes'))
    ordered_tariff = models.ForeignKey('Tariff',
                                       default=None,
                                       null=True,
                                       blank=True,
                                       on_delete=models.SET_DEFAULT,
                                       verbose_name=_('ordered tariff'))

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return (f"{gettext('order')} {gettext('#')} {str(self.num_id)} {gettext('from')} ") + \
               (f"{self.customer_name} ({self.phone_number})" if self.customer_name else self.phone_number)


class Tariff(BaseModel):
    title = models.CharField(max_length=16,
                             verbose_name=_('title'),
                             help_text=_("The maximum length is 16 characters"))
    slug = AutoSlugField(populate_from='title', unique=True)
    price = models.IntegerField(verbose_name=_('price'),
                                validators=[MinValueValidator(0), MaxValueValidator(99999)],
                                help_text=_("Value in the range from 0 to 99999"))
    price_prefix = models.BooleanField(default=False,
                                       verbose_name=_('price prefix'),
                                       help_text=_("Adds the preposition 'from' before the price"))
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    tariff_advantages = models.ManyToManyField('TariffAdvantage', verbose_name=_('tariff advantages'), blank=True)

    class Meta:
        verbose_name = _('tariff')
        verbose_name_plural = _('tariffs')
        ordering = ['price', 'num_id']

    def __str__(self):
        return self.title


class TariffAdvantage(BaseModel):
    title = models.CharField(max_length=50,
                             verbose_name=_('title'),
                             help_text=_("The maximum length is 50 characters"))
    ordering = models.IntegerField(default=0,
                                   verbose_name=_('ordering'),
                                   help_text=_("This parameter is used in ascending order to sort objects"))

    class Meta:
        verbose_name = _('tariff advantage')
        verbose_name_plural = _('tariff advantages')
        ordering = ['ordering', 'num_id']

    def __str__(self):
        return self.title
