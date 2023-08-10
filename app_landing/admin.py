from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from app_landing.models import Project, Category, Parameter


class BaseAdminMixin:
    ordering = ('-num_id',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('meta'), {"classes": ["collapse"],
                         "fields": [("created_by", "created_date"),
                                    ("updated_by", 'updated_date')], },),
            (_('identifiers'), {"fields": [('num_id', 'uuid')],
                                "classes": ["collapse"]}),
        ]
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            'num_id', 'uuid', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

        return readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.created_by:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
        obj.save()

# Register your models here.
@admin.register(Project)
class ProjectAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'title', 'category', 'is_active']
    list_display_links = ['title']
    list_filter = ['category', 'is_active']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'].append('slug')
        fieldsets += [
            (None, {"fields": ["title", "category", "description", 'is_active',]},),
        ]

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += [
            'slug',
        ]

        return readonly_fields


@admin.register(Category)
class CategoryAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'title', 'created_date', 'updated_date']
    list_display_links = ['title']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'].append('slug')
        fieldsets += [
            (None, {"fields": ["title"]},),
        ]

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += [
            'slug',
        ]

        return readonly_fields


@admin.register(Parameter)
class ParameterAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'title', 'value', 'created_date', 'updated_date']
    list_display_links = ['title']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += [
            (None, {"fields": ["title", "value", "project"]}),
        ]

        return fieldsets