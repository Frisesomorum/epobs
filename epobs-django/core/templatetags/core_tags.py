from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def to_list(*args):
    return args


@register.filter
def concat(arg1, arg2):
    return str(arg1) + str(arg2)
