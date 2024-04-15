from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

def percent_format(text, places=-1):
    """Operates as Django's built-in 'floatformat' filter, but adds a percent on the end 
    if valid."""
    floatformat_result = floatformat(text, places)
    if floatformat_result != "":
        return f"{floatformat_result}%"
    return ""

register.filter("percentformat", percent_format)
