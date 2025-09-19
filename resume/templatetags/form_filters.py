# resume/templatetags/form_filters.py
from django import template
register = template.Library()

@register.filter
def add_class(field, css):
    return field.as_widget(attrs={'class': css})

@register.filter
def add_textarea_class(field, css):
    attrs = {'class': css, 'rows': field.field.widget.attrs.get('rows', 12)}
    return field.as_widget(attrs=attrs)
