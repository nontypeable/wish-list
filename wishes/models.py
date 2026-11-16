from typing import ClassVar

from django.db import models
from django.db.models.query_utils import Q

from users.models import User


class WishList(models.Model):
    user = models.OneToOneField(User, verbose_name="владелец", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="название", max_length=255)

    class Meta:
        verbose_name: ClassVar[str] = "вишлист"
        verbose_name_plural: ClassVar[str] = "вишлисты"

    def __str__(self) -> str:
        return self.name


class Wish(models.Model):
    name = models.CharField(verbose_name="название", max_length=255)
    image = models.ImageField(
        verbose_name="изображение", upload_to="wishes/", null=True, blank=True
    )
    description = models.TextField(verbose_name="описание", blank=True)
    price = models.DecimalField(
        verbose_name="цена", max_digits=11, decimal_places=2, blank=True, null=True
    )
    where_can_buy = models.TextField(verbose_name="где можно купить", blank=True)
    fulfilled = models.BooleanField(verbose_name="исполнено", default=False)
    who_booked = models.ForeignKey(
        User,
        verbose_name="кто забронировал",
        on_delete=models.SET_NULL,
        related_name="booked_wishes",
        blank=True,
        null=True,
    )
    wish_list = models.ForeignKey(
        WishList, verbose_name="вишлист", on_delete=models.CASCADE, related_name="wishes"
    )

    class Meta:
        verbose_name: ClassVar[str] = "желание"
        verbose_name_plural: ClassVar[str] = "желания"

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
        verbose_name="вишлист",
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    invited_email = models.EmailField(verbose_name="электронная почта приглашённого")
    code_hash = models.CharField(verbose_name="хэш кода приглашения", max_length=64, unique=True)
    accepted_at = models.DateTimeField(verbose_name="дата принятия", null=True, blank=True)

    class Meta:
        verbose_name: ClassVar[str] = "приглашение в вишлист"
        verbose_name_plural: ClassVar[str] = "приглашения в вишлисты"

    def __str__(self) -> str:
        return self.wish_list.name


class AvailableWishList(models.Model):
    wish_list = models.ForeignKey(
        WishList,
        verbose_name="вишлист",
        on_delete=models.CASCADE,
        related_name="accesses",
    )
    user = models.ForeignKey(
        User,
        verbose_name="пользователь с доступом",
        on_delete=models.CASCADE,
        related_name="wish_list_accesses",
    )

    class Meta:
        verbose_name: ClassVar[str] = "доступ к вишлисту"
        verbose_name_plural: ClassVar[str] = "доступы к вишлистам"

    def __str__(self) -> str:
        return self.wish_list.name
