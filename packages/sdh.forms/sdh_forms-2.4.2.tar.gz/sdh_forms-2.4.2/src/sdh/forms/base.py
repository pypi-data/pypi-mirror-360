import warnings

from django import forms
from django.forms import BoundField
from django.template import loader
from .conf import settings


class BaseForm:
    use_required_attribute = False

    _ref_class = None
    template = 'sdh/forms/form.html'

    def __init__(self, *kargs, **kwargs):
        """
        Init accept two additional arguments:
        request - http request from view
        template - optional template name
        """
        assert self._ref_class is not None

        self._request = kwargs.pop('request', None)
        self.template = kwargs.pop('template', self.template)

        super(self._ref_class, self).__init__(*kargs, **kwargs)

        for field in self.fields.values():
            field._request = self.request

        self.ajax_fields_populate()

    def ajax_fields_populate(self):
        for name, field in self.fields.items():
            if hasattr(field, 'ajax_populate'):
                field.ajax_populate(self, name)

    @property
    def request(self):
        return self._request

    def get_value_for(self, field_name):
        """ used to obtain value of fields

            useful when need get value not depend on form state
        """
        if self.is_bound:
            return self[field_name].data
        return self.initial.get(field_name, self.fields[field_name].initial)

    def output_via_template(self):
        if hasattr(self, 'get_template_name'):
            warnings.warn('Use form.get_template_name deprecated. use form.template property')
            _template_name = self.get_template_name()
        else:
            _template_name = self.template
        " Helper function for fieldstring fields data from form. "
        bound_fields = [BoundField(self, field, name) for name, field in self.fields.items()]

        c = dict(form=self, bound_fields=bound_fields)
        t = loader.get_template(_template_name)
        return t.render(c)

    def as_template(self):
        """" {{ form.as_template }} """
        for field in self.fields.keys():
            self.fields[field].str_class = str(self.fields[field].widget.__class__.__name__)
        return self.output_via_template()

    def populate(self, field_name, queryset, add_empty=False, label_name=None,
                 value_name=None, empty_label=None, empty_value=None):
        """ Populate choice field by given QuerySet
        Args:
            field_name: field name in form (as string)
            queryset: QuerySet object
            add_empty: if set to True function prepend list of
                choices by empty line
            label_name: name of field, property or method in queryset
                instance model, that will be set as label in dropdown
            value_name: name of field, property or method in queryset
                instance model, that will be set as value in dropdown
            empty_label: value, that will be set for empty line,
                by default it set to settings.DEFAULT_CHOICE_LABEL
            empty_value: value, that will be set for empty line,
                by default it set to ''

        """
        field = self.fields[field_name]

        choices = []
        if add_empty:
            choices.append((empty_value or '',
                            empty_label if empty_label is not None else settings.DEFAULT_CHOICE_LABEL))

        def _get_field(obj, fieldname=None):
            if fieldname:
                value = getattr(obj, fieldname)
                if callable(value):
                    value = value()
            else:
                value = str(obj)
            return value

        for item in queryset:
            if callable(label_name):
                label = label_name(item)
            else:
                label = _get_field(item, label_name)
            value = _get_field(item, value_name or 'pk')
            choices.append((str(value), label))

        field.choices = choices

    def set_field_error(self, field_name, error):
        warnings.warn("Calling init method is Deprecated. Please use add_error method", DeprecationWarning)
        self.add_error(field_name, error)

    def set_non_field_error(self, error):
        self.add_error(forms.forms.NON_FIELD_ERRORS, error)
