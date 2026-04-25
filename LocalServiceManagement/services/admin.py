from django.contrib import admin
from .models import Service, Review, Category, VendorProfile, ServiceImage

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ['image']

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor', 'name', 'price', 'rating', 'created_at']
    list_filter = ['created_at', 'price', 'rating', 'vendor']
    search_fields = ['title', 'name', 'description', 'vendor__email']
    inlines = [ServiceImageInline]
    
    fieldsets = (
        ('Service Information', {
            'fields': ('title', 'name', 'vendor')
        }),
        ('Details', {
            'fields': ('description', 'price', 'image')
        }),
        ('Category', {
            'fields': ('category',) if hasattr(Service, 'category') else ()
        }),
        ('Ratings', {
            'fields': ('rating', 'rating_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['rating', 'rating_count', 'created_at', 'updated_at']
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Remove Category fieldset if field doesn't exist
        return [(name, options) for name, options in fieldsets if options['fields']]

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['service', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'service']
    search_fields = ['service__title', 'user__email', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('service', 'user', 'rating')
        }),
        ('Comment', {
            'fields': ('comment',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'verified', 'experience']
    list_filter = ['verified', 'created_at']
    search_fields = ['user__email', 'phone', 'address']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'verified')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Professional', {
            'fields': ('experience',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Service, ServiceAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)
