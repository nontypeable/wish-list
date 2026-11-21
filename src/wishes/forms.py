from typing import TYPE_CHECKING, ClassVar

from django import forms

from .models import Wish, WishListInvitation

if TYPE_CHECKING:
    BaseWishForm = forms.ModelForm[Wish]
else:
    BaseWishForm = forms.ModelForm


class CreateWishForm(BaseWishForm):
    class Meta:
        model = Wish
        fields: ClassVar[tuple[str, ...]] = (
            "name",
            "image",
            "description",
            "price",
            "where_can_buy",
        )
        labels: ClassVar[dict[str, str]] = {
            "name": "Название",
            "image": "Изображение",
            "description": "Описание",
            "price": "Цена",
            "where_can_buy": "Где можно купить",
        }


if TYPE_CHECKING:
    BaseCreateInvitationForm = forms.ModelForm[WishListInvitation]
else:
    BaseCreateInvitationForm = forms.ModelForm


class CreateInvitationForm(BaseCreateInvitationForm):
    class Meta:
        model = WishListInvitation
        fields: ClassVar[tuple[str, ...]] = ("invited_email",)
        labels: ClassVar[dict[str, str]] = {"invited_email": "Электронная почта получателя"}
