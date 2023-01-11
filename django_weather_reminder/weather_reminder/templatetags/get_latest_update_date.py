from django import template

from weather_reminder.models import LastUpdateTime

register = template.Library()


@register.simple_tag
def get_latest_update_date():
    last_update = LastUpdateTime.objects.first()
    if last_update is None:
        return None

    return last_update.updated
