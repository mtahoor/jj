from django import template
from django.contrib.messages import get_messages

register = template.Library()

@register.inclusion_tag('includes/message_tags.html', takes_context=True)
def render_messages(context):
    """
    Renders Django messages as hidden elements that can be processed by JavaScript.
    """
    return {
        'messages': get_messages(context['request']),
    }
