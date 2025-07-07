import logging
import uuid

from django.core.exceptions import FieldError
from django.db import models


class GenericBaseModel(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, null=False, editable=False, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def model_to_dict(self) -> dict:
        try:
            return {
                field.name: getattr(self, field.name) for field in self._meta.fields
            }
        except Exception:
            logging.error("Error occurred  while converting models to dict")
            raise FieldError("Error occurred  while converting models to dict")
