from django.conf import settings
from django.http import Http404, HttpResponsePermanentRedirect
from django.template.response import TemplateResponse
from django.utils.http import escape_leading_slashes

import requests

from .models import find_route


def page_view(request, path):
    m = find_route(path)
    if m is None:
        if settings.APPEND_SLASH and not path.endswith('/'):
            m = find_route(f'{path}/')
            if m is not None:
                new_path = request.get_full_path(force_append_slash=True)
                new_path = escape_leading_slashes(new_path)
                return HttpResponsePermanentRedirect(new_path)
        raise Http404

    data = None
    if m.route.endpoint:
        endpoint, params = m.build(allow_preview=settings.ALLOW_PREVIEW)
        r = requests.get(endpoint, params=params)
        if r.status_code == 404:
            raise Http404
        r.raise_for_status()
        data = r.json()

    return TemplateResponse(request, m.route.template_name, {
        'data': data,
    })
