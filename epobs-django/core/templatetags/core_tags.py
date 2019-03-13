from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

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


@register.filter('klass')
def klass(ob):
    return ob.__class__.__name__


def currency(amount):
    negative = (amount < 0)
    amount = abs(round(float(amount), 2))
    formatted_abs_value = "$%s%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-3:])
    if negative:
        return "(%s)" % (formatted_abs_value)
    return formatted_abs_value


register.filter('currency', currency)
