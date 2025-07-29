from django.conf import settings
from django.forms.widgets import Input, Select, SelectMultiple, DateInput
from django.utils import formats
from .conf import settings


class SelectCallback(Select):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices_callback = None

    def render(self, name, value, attrs=None, renderer=None):
        self.choices = list(self.choices_callback())
        return super(SelectCallback, self).render(name, value, attrs, renderer)


class SelectCallbackMultiple(SelectCallback, SelectMultiple):
    pass


class DatePickerWidget(DateInput):
    DATE_PICKER_FORMAT = 'DATE_PICKER_FORMAT'
    DATE_PICKER_CLASS = settings.DATE_PICKER_CLASS

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super(DatePickerWidget, self).build_attrs(base_attrs, extra_attrs)
        attrs['class'] = attrs.get('class', '') + ' %s' % self.DATE_PICKER_CLASS
        attrs['data-date-autoclose'] = 'true'
        date_format = formats.get_format(self.DATE_PICKER_FORMAT)
        attrs['data-date-format'] = getattr(settings, self.DATE_PICKER_FORMAT,
                                            'YYYY-MM-DD') if date_format == self.DATE_PICKER_FORMAT else date_format
        return attrs


class Select2AjaxWidget(Select):

    def __init__(self, attrs=None, choices=(), add_empty=False, data_url=None):
        self.add_empty = add_empty
        self.data_url = data_url
        super().__init__(attrs=attrs, choices=choices)

    def build_attrs(self, *args, **kwargs):
        """
        Set select2's AJAX attributes.
        """
        attrs = super(Select2AjaxWidget, self).build_attrs(*args, **kwargs)
        if 'class' in attrs:
            attrs['class'] += ' select2'
        else:
            attrs['class'] = 'select2'
        if self.add_empty:
            attrs.setdefault('data-allow-clear', 'true')
        else:
            attrs.setdefault('data-allow-clear', 'false')
        if self.data_url:
            attrs.setdefault('data-ajax--url', self.data_url)
        attrs.setdefault('data-ajax--cache', 'false')
        attrs.setdefault('data-ajax--type', 'GET')
        attrs.setdefault('data-minimum-input-length', 0)
        return attrs


class Select2AjaxMultipleWidget(Select2AjaxWidget, SelectMultiple):
    pass


class LabelWidget(Input):
    input_type = 'text'
    template_name = 'sdh/forms/widgets/label_input.html'

    def __init__(self, attrs=None, choices=(), empty_label=None):
        super().__init__(attrs)
        # choices can be any iterable, but we may need to render this widget
        # multiple times. Thus, collapse it into a list so it can be consumed
        # more than once.
        self.empty_label = empty_label or ''
        self.choices = list(choices)

    def get_context(self, name, value, attrs):
        context = super(Input, self).get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        context['widget']['label'] = self.get_label(context['widget']['value'])
        return context

    def get_label(self, value):
        for v, l in self.choices:
            if v == value:
                return l
        return value or self.empty_label


class MultipleLabelWidget(LabelWidget):
    template_name = 'sdh/forms/widgets/multiple_label_input.html'

    def get_context(self, name, value, attrs):
        context = super(LabelWidget, self).get_context(name, value, attrs)
        final_attrs = context['widget']['attrs']
        id_ = context['widget']['attrs'].get('id')

        subwidgets = []
        for index, value_ in enumerate(context['widget']['value']):
            widget_attrs = final_attrs.copy()
            if id_:
                # An ID attribute was given. Add a numeric index as a suffix
                # so that the inputs don't all have the same ID attribute.
                widget_attrs['id'] = '%s_%s' % (id_, index)
            widget = LabelWidget(choices=self.choices, empty_label=self.empty_label)
            widget.is_required = self.is_required
            subwidgets.append(widget.get_context(name, value_, widget_attrs)['widget'])

        context['widget']['subwidgets'] = subwidgets
        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)

    def format_value(self, value):
        return [] if value is None else value
