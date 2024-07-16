from django import template
from event.models import Square
from event.models import genomeEntry

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg


def tuple_length(value):
    return len(value)

@register.filter(name='get_square')
def get_square(x_value, y_value):
    square = Square.objects.filter(x=x_value, y=y_value).first()
    return square

@register.filter(name='get_selGens')
def get_selGens():
    selg = genomeEntry.objects.all()
    return selg
