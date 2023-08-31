from typing import Any

from django.core import checks
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Model


class OrderField(models.PositiveIntegerField):
    description = "Ordering field"

    def __init__(self, unique_for_field=None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.unique_for_field = unique_for_field

    def check(self, **kwargs):
        return [*super().check(**kwargs), *self._check_for_field_attr(**kwargs)]

    def _check_for_field_attr(self, **kwargs):
        if self.unique_for_field is None:
            return [
                checks.Error("OrderField must define a 'unique_for_field' attribute")
            ]
        elif self.unique_for_field not in [
            f.name for f in self.model._meta.get_fields()
        ]:
            return [checks.Error("OrderField enterred does not mach")]

        return []

    def pre_save(self, model_instance, add) -> Any:
        if getattr(model_instance, self.attname) is None:
            qs = self.model.objects.all()
            try:
                query = {
                    self.unique_for_field: getattr(
                        model_instance, self.unique_for_field
                    )
                }
                qs = qs.filter(**query)
                last_item = qs.latest(self.attname)
                value = last_item.order + 1

            except ObjectDoesNotExist:
                value = 1

            return value
        else:
            return super().pre_save(model_instance=model_instance, add=add)
