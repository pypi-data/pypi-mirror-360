from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe

from favicon.models import Favicon

register = template.Library()


@register.simple_tag(takes_context=True)
def place_favicon(context):
    """
    Gets Favicon-URL for the Model.

    Template Syntax:

        {% place_favicon %}

    """

    fav = Favicon.on_site.filter(isFavicon=True).first()
    if not fav:
        return mark_safe('<!-- no favicon -->')
 
    html = fav.as_html()
    return mark_safe(html)
