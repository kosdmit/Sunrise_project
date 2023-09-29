from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from app_landing.models import Project, Category, Parameter, ProjectImage, \
    Order, Tariff, TariffAdvantage


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


class ParameterInlineAdmin(admin.TabularInline):
    model = Parameter
    extra = 1


class ProjectImageInlineAdmin(admin.StackedInline):
    model = ProjectImage
    fields = ('ordering', ('image', 'image_preview'), ('title', 'description'))
    readonly_fields = ('image_preview',)
    ordering = ('ordering', 'num_id')
    extra = 1

    def image_preview(self, obj):
        # TODO: add right proportions support for image preview
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="80"/>'
            )
        return '-'

    image_preview.short_description = _('image preview')


class TariffListFilter(admin.SimpleListFilter):
    title = _('tariff')
    parameter_name = 'tariff'

    def lookups(self, request, model_admin):
        tariffs = Tariff.objects.all()
        return [(tariff.id, tariff.title) for tariff in tariffs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tariff__tariffadvantages__id=self.value())
        return queryset


# Register your models here.
@admin.register(Project)
class ProjectAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'title', 'category', 'is_active', 'is_featured']
    list_display_links = ['title']
    list_filter = ['category', 'is_active']
    inlines = [ParameterInlineAdmin, ProjectImageInlineAdmin]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'].append('slug')
        fieldsets += [
            (None, {"fields": [
                "title",
                "category",
                "description",
                ('is_active', 'is_featured', 'to_show_download_date'),
            ]},),
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


@admin.register(Order)
class OrderAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['num_id', 'customer_name', 'phone_number', 'status', ]
    list_display_links = ['phone_number']
    list_filter = ['status', ]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += [
            (None, {"fields": ["customer_name", "phone_number", "note", "status"]}),
        ]

        return fieldsets


@admin.register(Tariff)
class TariffAdmin(BaseAdminMixin, admin.ModelAdmin):
    ordering = ['price', 'num_id']
    list_display = ['num_id', 'title', 'price', ]
    list_display_links = ['title']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'].append('slug')
        fieldsets += [
            (None, {"fields": ["title",
                               ("price_prefix", "price"),
                               "description",
                               "tariff_advantages"]}),
        ]

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields += [
            'slug',
        ]

        return readonly_fields

    def has_add_permission(self, request):
        if Tariff.objects.count() >= 3:
            return False
        else:
            return True


@admin.register(TariffAdvantage)
class TariffAdvantageAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ['ordering', 'num_id', 'title', ]
    list_display_links = ['title']
    ordering = ['ordering', 'num_id']
    list_filter = (TariffListFilter,)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += [
            (None, {"fields": ["title", "ordering"]}),
        ]

        return fieldsets

