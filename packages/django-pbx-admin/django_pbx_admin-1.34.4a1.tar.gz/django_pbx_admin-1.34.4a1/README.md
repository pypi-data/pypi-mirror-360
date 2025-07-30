# Pbx Admin

Django Printbox admin interface

## Release

Just add tag with version number (ie. 1.2.3) to release.

## Settings

To proper display error messages, you have to setup message tags like these.

```python
from django.contrib import messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
```

## CSS Compiling

1. Install SASS from https://sass-lang.com/install
2. Run ./scripts/css_compile.sh

## Local development

1. Activate pbx2 viertual environment
2. Install local django-pbx-admin `pip install -e .`
3. Add project folder as content root (in PyCharm Settings > Project > Project Structure -> Add Content Root)

