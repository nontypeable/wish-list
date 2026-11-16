from typing import ClassVar

from django.db import models
from django.db.models.query_utils import Q

from users.models import User


class WishList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Wish(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="wishes/", null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    where_can_buy = models.TextField(blank=True)
    fulfilled = models.BooleanField(default=False)
    who_booked = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="booked_wishes", blank=True, null=True
    )
    wish_list = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name="wishes")

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_price_ge_0", condition=Q(price__gte=0)
            ),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def is_booked(self) -> bool:
        return self.who_booked is not None


class WishListInvitation(models.Model):
    wish_list = models.ForeignKey(
        WishList,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    invited_email = models.EmailField()
    code_hash = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return self.wish_list.name


class AvailableWishList(models.Model):
    wish_list = models.ForeignKey(
        WishList,
        on_delete=models.CASCADE,
        related_name="accesses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wish_list_accesses",
    )

    def __str__(self) -> str:
        return self.wish_list.name
