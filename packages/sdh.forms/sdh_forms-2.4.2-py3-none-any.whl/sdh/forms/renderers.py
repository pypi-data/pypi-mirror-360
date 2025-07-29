from pathlib import Path

from django.template.backends.django import DjangoTemplates
from django.forms import renderers
from django.conf import settings
from django.utils.functional import cached_property


DEFAULT_SETTINGS = {
    'APP_DIRS': True,
    'DIRS': [],
    'NAME': 'djangoforms',
    'OPTIONS': {},
}


class SdhFormRenderer(renderers.BaseRenderer):
    backend = DjangoTemplates

    def get_template(self, template_name):
        return self.engine.get_template(template_name)

    @cached_property
    def engine(self):
        try:
            _settings = settings.SDH_RENDERER.copy()
        except AttributeError:
            _settings = DEFAULT_SETTINGS.copy()

        _settings['DIRS'].append(Path(renderers.__file__).parent / self.backend.app_dirname)
        return self.backend(_settings)
