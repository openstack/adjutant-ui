# Making use of this to make a generic enabled file
# to load base adjutant-ui content.
FEATURE = "adjutant-ui-base"

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'adjutant_ui',
    'overextends',
]

# TODO(adriant): Remove this and overextends when we drop django<1.11
from distutils.version import StrictVersion # noqa
import django # noqa

if StrictVersion(django.__version__) >= StrictVersion("1.9"):
    from openstack_dashboard.settings import TEMPLATES as _TEMPLATES

    _builtin = 'overextends.templatetags.overextends_tags'
    _template_backend = 'django.template.backends.django.DjangoTemplates'

    for _backend in _TEMPLATES:
        if _backend['BACKEND'] == _template_backend:
            if 'OPTIONS' in _backend:
                try:
                    if _builtin not in _backend['OPTIONS']['builtins']:
                        _backend['OPTIONS']['builtins'].append(_builtin)
                except KeyError:
                    _backend['OPTIONS']['builtins'] = [_builtin, ]
            else:
                _backend['OPTIONS'] = {
                    'builtins': [_builtin, ]
                }
            break
