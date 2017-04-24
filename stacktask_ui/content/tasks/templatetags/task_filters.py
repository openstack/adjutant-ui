from django import template
import json

register = template.Library()


@register.simple_tag
def pretty_json(value):
    return json.dumps(value, indent=4)


@register.simple_tag
def pretty_list(value):
    return ', '.join(value)


register.filter('pretty_json', pretty_json)
register.filter('pretty_list', pretty_list)
