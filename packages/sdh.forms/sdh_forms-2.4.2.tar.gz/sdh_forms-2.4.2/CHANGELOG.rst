Changelog
=========

version 2.4.2
  * added support of Django 5

version 2.4.1
 * added support of Django 4.2
 * moved build from setup.py to pyproject.toml

version 2.4.0
 * added option to select differect css-class for date-picker
 * added ModelChoiceField

version 2.3.0
 * added sdh.form.conf module with option to manage default empty label
 * added compatibility for Django 3.2
 * removed python2 compatibility

version 2.2.8
 * remove python2 compatibility
 * minimal Django version 2.2

version 2.2.7
 * AjaxTypedChoiceField catch ObjectDoesNotExists and raise validation error

version 2.2.6
 * added template tag sdh_split_column

version 2.2.5
 * fix Many2Many relations

version 2.2.4
 * disable HTML require field option by default

version 2.2.3
 * fix caching query result in RelatedChoiceFieldMixin

version 2.2.2
 * fix populate values for AjaxChoiceFieldMixin

version 2.2.1
 * change hidden behavior for LabelWidget

version 2.2.0
 * added SdhFormRenderer
   for override default Django settings use
   ```
   FORM_RENDERER = 'sdh.forms.renderers.SdhFormRenderer'
   ```
   Renderered settings placed under SDH_RENDERER option in the settings.py


version 2.1.0
 * improved LabelWidget
 * fixed default field template

version 2.0.1
 * fix imports

version 2.0.0
 * drop prior Django 1.11 compatibility
 * fix LabelWidget work with Django 1.11

version 1.2.2
 * add AjaxChoice fields

version 1.2.1
 * prevent populate choices for ajax select widget

version 1.2.0
 * Added RelatedMultipleChoiceField; code refactoring

version 1.1.2
 * Added RelatedChoiceField.choices setter

version 1.1.0
 * Added Select2AjaxWidget and AjaxTypedChoiceField

version 1.0.1
 * Added backward compatibility with method get_template_name with raising deprecated warnings

version 1.0.0
 * Fork project ua2.forms and break backward compatibility with prior Django 1.8
