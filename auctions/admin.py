from django.contrib import admin

from .models import Auction, Bid


class BidInline(admin.TabularInline):
    model = Bid
    extra = 1


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("product", "start_time", "end_time", "current_price", "status")
    list_filter = ("status",)
    search_fields = ("product__title",)
    inlines = [BidInline]


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("auction", "bidder", "amount", "created_at")
    search_fields = ("auction__product__title", "bidder__username")
# Register your models here.
