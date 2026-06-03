from django.contrib import admin
from .models import Listing, ListingTitle, ListingLocation, ListingImage

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

class ListingTitleInline(admin.TabularInline):
    model = ListingTitle
    extra = 1

class ListingLocationInline(admin.TabularInline):
    model = ListingLocation
    extra = 1

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "condition", "price", "created_at")
    inlines = [ListingTitleInline, ListingLocationInline, ListingImageInline]
