"""
Settings for sdh.forms

SDH_FORMS = {
    'DEFAULT_CHOICE_LABEL': '-------',
}
"""
from django.conf import settings as django_settings


DEFAULTS = {
    'DEFAULT_CHOICE_LABEL': '-------',
    'DATE_PICKER_CLASS': 'date-picker',
}


class FormsSettings:
    def __init__(self, defaults=None):
        self.defaults = defaults or DEFAULTS

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid setting: '%s'" % attr)

        try:
            val = django_settings.SDH_FORMS[attr]
        except (KeyError, AttributeError):
            val = self.defaults[attr]
        return val


settings = FormsSettings(DEFAULTS)
