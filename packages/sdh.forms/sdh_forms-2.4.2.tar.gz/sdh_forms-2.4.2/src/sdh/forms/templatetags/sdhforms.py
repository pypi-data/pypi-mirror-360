import math
from django import template

register = template.Library()


@register.simple_tag
def sdh_render_field(bound_field, **attrs):
    widget = bound_field.field.widget

    attrs['class'] = widget.attrs.get('class', '') + ' ' + attrs.get('class', '')

    if bound_field.field.show_hidden_initial:
        return bound_field.as_widget(attrs=attrs) + bound_field.as_hidden(only_initial=True)
    return bound_field.as_widget(attrs=attrs)


@register.simple_tag
def sdh_split_column(columns, row_qty=6, col_qty=4):
    columns = list(columns)
    step = int(math.ceil(len(columns)/float(col_qty)))
    if step < row_qty:
        step = row_qty
    for i in range(0, len(columns), step):
        yield columns[i:i + step]
