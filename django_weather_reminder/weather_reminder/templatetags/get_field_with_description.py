from typing import NamedTuple

from django import template
from django.db.models import Model

register = template.Library()


class FieldWithDescription(NamedTuple):
    description: str
    value: any


@register.simple_tag
def get_field_with_description(instance: Model, field_name: str) -> FieldWithDescription:
    """
    Returns model instance field value with field description
    :param instance: model instance
    :param field_name:
    :return: named tuple -  a field description from the model field help text and a field value

    """
    return FieldWithDescription(
        description=type(instance)._meta.get_field(field_name).help_text,
        value=getattr(instance, field_name)
    )
