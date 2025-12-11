from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica value por arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sum_attr(queryset, attr):
    """Suma un atributo de un queryset"""
    try:
        total = 0
        for obj in queryset:
            if hasattr(obj, attr):
                total += getattr(obj, attr)
        return total
    except:
        return 0

@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario"""
    return dictionary.get(key)

@register.filter
def divide(value, arg):
    """Divide value por arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def groupby(queryset, attr):
    """Agrupa un queryset por atributo"""
    from itertools import groupby
    from operator import attrgetter
    
    try:
        sorted_queryset = sorted(queryset, key=attrgetter(attr))
        return {key: list(group) for key, group in groupby(sorted_queryset, key=attrgetter(attr))}
    except:
        return {}