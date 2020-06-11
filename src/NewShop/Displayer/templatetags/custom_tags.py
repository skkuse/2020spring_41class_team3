from django import template
register = template.Library()

@register.filter
def index(lst, index):
    return lst[index]