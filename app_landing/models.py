import uuid

from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from app_landing.models_mixins import CompressImageBeforeSaveMixin

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
    description = models.TextField(verbose_name=_('description'), null=True)
    is_featured = models.BooleanField(verbose_name=_('is featured project'), default=False)

    def save(self, *args, **kwargs):
        if self.is_featured:
            Project.objects.filter(is_featured=True).update(is_featured=False)

        super(Project, self).save(*args, **kwargs)

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
    caption = models.CharField(max_length=150, blank=True, verbose_name=_('caption'))
    slug = AutoSlugField(populate_from='caption', unique=True)
    order = models.IntegerField(default=0, verbose_name=_('order'))

    class Meta:
        verbose_name = _('project image')
        verbose_name_plural = _('project images')
        ordering = ['order', 'num_id']

    def __str__(self):
        return self.caption

