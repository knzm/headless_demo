from django.conf import settings
from django.http import Http404
from django.template.response import TemplateResponse

import requests


def index(request):
    params = {
        'fields': '*',
    }
    if settings.ALLOW_PREVIEW:
        params['draft'] = '1'
    r = requests.get(f'http://localhost:18000/api/v1/blogs/', params=params)
    data = r.json()
    pages = [item for item in data['items']]
    return TemplateResponse(request, 'blog_index.html', {
        'pages': pages,
    })


def detail(request, blog_id):
    params = {
        'fields': '*',
    }
    if settings.ALLOW_PREVIEW:
        params['draft'] = '1'
    r = requests.get(f'http://localhost:18000/api/v1/blogs/{blog_id}', params=params)
    if r.status_code == 404:
        raise Http404
    r.raise_for_status()
    page = r.json()
    return TemplateResponse(request, 'blog_page.html', {
        'page': page,
    })
