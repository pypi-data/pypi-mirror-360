# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Generic, TypeVar

from ._models import GenericModel

__all__ = ["ItemsWrapper"]

_T = TypeVar("_T")


class ItemsWrapper(GenericModel, Generic[_T]):
    items: _T

    @staticmethod
    def _unwrapper(obj: "ItemsWrapper[_T]") -> _T:
        return obj.items
