from django.forms import formsets, IntegerField, BooleanField
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import ORDERING_FIELD_NAME, DELETION_FIELD_NAME


class RequestFormSet(formsets.BaseFormSet):
    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request', None)
        self.form_args = kwargs.pop('args', [])

        super(RequestFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {
            'auto_id': self.auto_id,
            'prefix': self.add_prefix(i),
            'error_class': self.error_class,
            }
        if self.is_bound:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial and 'initial' not in kwargs:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        defaults['request'] = self._request

        form = self.form(*self.form_args, **defaults)
        self.add_fields(form, i)
        return form

    @property
    def empty_form(self):
        form = self.form(
            *self.form_args,
            auto_id=self.auto_id,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,
            request=self._request)
        self.add_fields(form, None)
        return form

    def add_fields(self, form, index):
        """A hook for adding extra fields on to each form instance."""
        if self.can_order:
            # Only pre-fill the ordering field for initial forms.
            if index is not None and index < self.initial_form_count() and ORDERING_FIELD_NAME not in form.fields:
                form.fields[ORDERING_FIELD_NAME] = IntegerField(label=_('Order'), initial=index + 1, required=False)
            elif index is not None and index < self.initial_form_count() and ORDERING_FIELD_NAME in form.fields:
                form.fields[ORDERING_FIELD_NAME].initial = index + 1
            elif ORDERING_FIELD_NAME not in form.fields:
                form.fields[ORDERING_FIELD_NAME] = IntegerField(label=_('Order'), required=False)
        if self.can_delete and DELETION_FIELD_NAME not in form.fields:
            form.fields[DELETION_FIELD_NAME] = BooleanField(label=_('Delete'), required=False)
