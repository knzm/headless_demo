from django.conf import settings
from django.http import Http404
from django.template.response import TemplateResponse

import requests

from .models import find_route


def page_view(request, path):
    m = find_route(path)
    if m is None:
        raise Http404

    params = {
        'fields': '*',
    }
    if settings.ALLOW_PREVIEW:
        params['draft'] = '1'

    endpoint = m.route.endpoint.format(**m.url_params)
    r = requests.get(endpoint, params=params)
    if r.status_code == 404:
        raise Http404
    r.raise_for_status()

    return TemplateResponse(request, m.route.template_name, {
        'data': r.json(),
    })
