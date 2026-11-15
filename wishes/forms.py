from typing import ClassVar

from django import forms

from .models import Wish


class CreateWishForm(forms.ModelForm):
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
