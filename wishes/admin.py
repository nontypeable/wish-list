from typing import TYPE_CHECKING

from django.contrib import admin

from wishes.models import AvailableWishList, Wish, WishList, WishListInvitation

if TYPE_CHECKING:
    BaseWishAdmin = admin.ModelAdmin[Wish]
    BaseWishInline = admin.TabularInline[Wish, WishList]
    BaseWishListAdmin = admin.ModelAdmin[WishList]
    BaseInvitationAdmin = admin.ModelAdmin[WishListInvitation]
    BaseAccessAdmin = admin.ModelAdmin[AvailableWishList]
else:
    BaseWishAdmin = admin.ModelAdmin
    BaseWishInline = admin.TabularInline
    BaseWishListAdmin = admin.ModelAdmin
    BaseInvitationAdmin = admin.ModelAdmin
    BaseAccessAdmin = admin.ModelAdmin


@admin.register(Wish)
class WishAdmin(BaseWishAdmin):
    list_display = ("id", "name", "price", "fulfilled", "wish_list__user__email")
    list_display_links = ("id", "name")
    list_filter = ("fulfilled",)
    search_fields = ("name", "wish_list__user__email")
    ordering = ("-id",)
    list_per_page = 50
    list_select_related = ("wish_list__user",)
    fieldsets = (
        (
            "Желание",
            {"fields": ("name", "description", "image")},
        ),
        (
            "Покупка",
            {"fields": ("price", "where_can_buy")},
        ),
        (
            "Состояние",
            {"fields": ("wish_list", "fulfilled", "who_booked")},
        ),
    )


class WishInline(BaseWishInline):
    model = Wish
    fields = ("id", "name", "price", "fulfilled")
    readonly_fields = ("id", "name", "price", "fulfilled")
    extra = 0
    show_change_link = True


@admin.register(WishList)
class WishListAdmin(BaseWishListAdmin):
    list_display = ("id", "name", "user__email")
    list_display_links = ("id", "name")
    search_fields = ("name", "user__email")
    inlines = (WishInline,)
    ordering = ("-id",)
    list_per_page = 50
    fieldsets = (
        ("Информация", {"fields": ("name",)}),
        ("Владелец", {"fields": ("user",)}),
    )


@admin.register(WishListInvitation)
class WishListInvitationAdmin(BaseInvitationAdmin):
    list_display = ("id", "invited_email", "wish_list__user__email", "accepted_at")
    search_fields = ("invited_email", "wish_list__user__email")
    ordering = ("-id",)
    list_per_page = 50


@admin.register(AvailableWishList)
class AvailableWishListAdmin(BaseAccessAdmin):
    list_display = ("id", "wish_list__user__email", "user__email")
    ordering = ("-id",)
    list_per_page = 50
