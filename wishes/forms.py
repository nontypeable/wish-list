from typing import TYPE_CHECKING, ClassVar

from django import forms

from .models import Wish

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
