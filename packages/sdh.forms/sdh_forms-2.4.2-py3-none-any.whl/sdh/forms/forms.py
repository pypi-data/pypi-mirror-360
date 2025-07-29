from django import forms
from django.db import models
from django.db.models.fields import Field

try:
    from django.db.models.fields import FieldDoesNotExist
except ImportError:
    from django.core.exceptions import FieldDoesNotExist

from django.db.models.manager import Manager

from .base import BaseForm


class RequestModelForm(BaseForm, forms.ModelForm):
    _ref_class = forms.ModelForm


class RequestForm(BaseForm, forms.Form):
    _ref_class = forms.Form

    def set_model_fields(self, instance, exclude_fields=None):
        """
        Fills values from the form fields into instance fields
        """
        exclude = exclude_fields or []
        data = self.cleaned_data

        model_fields = [item.name for item in instance._meta.get_fields() if isinstance(item, Field)]

        for key in data:
            if key in model_fields and key not in exclude:
                field = instance._meta.get_field(key)
                if isinstance(field, (models.ImageField, models.FileField)):
                    if data[key] is not None:
                        if data[key] is False:
                            data[key] = None
                        setattr(instance, key, data[key])
                elif isinstance(field, (models.ForeignKey, models.IPAddressField, models.GenericIPAddressField)):
                    if data[key]:
                        setattr(instance, key, data[key])
                    else:
                        setattr(instance, key, None)
                elif isinstance(field, models.ManyToManyField):
                    getattr(instance, key).set(data[key])
                else:
                    setattr(instance, key, data[key])

    def set_initial(self, instance):
        """
        Different to models_to_dict = source of field list
        :param instance:
        :return:
        """
        for fieldname in self.fields.keys():
            field = self.fields[fieldname]
            try:
                model_field = instance._meta.get_field(fieldname)
            except FieldDoesNotExist:
                continue

            if fieldname in self.initial:
                continue
            if hasattr(instance, fieldname):
                attr = getattr(instance, fieldname)
                if callable(attr) and not issubclass(attr.__class__, Manager):
                    attr = attr()

                if attr is None:
                    continue

                if isinstance(field, forms.ModelMultipleChoiceField):
                    self.initial[field] = attr.all()
                elif isinstance(model_field, models.ManyToManyField):
                    self.initial[fieldname] = [t.pk for t in attr.all()]
                elif isinstance(model_field, models.ForeignKey):
                    self.initial[fieldname] = attr.pk
                else:
                    self.initial[fieldname] = attr
        self.ajax_fields_populate()


class SaveModelForm(RequestForm):
    model = None

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance:
            self.set_initial(self.instance)

    def save(self):
        instance = self.instance or self.model()
        self.set_model_fields(instance)
        instance.save()
        return instance
