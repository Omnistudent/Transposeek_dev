from django import template
from event.models import genomeEntry

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg


def tuple_length(value):
    return len(value)



@register.filter(name='get_selGens')
def get_selGens():
    selg = genomeEntry.objects.all()
    return selg
