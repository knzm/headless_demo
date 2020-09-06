import re
import urllib.parse

from django.db import models
from django.urls import get_script_prefix
from django.urls.exceptions import NoReverseMatch
from django.urls.resolvers import _route_to_regex
from django.utils.regex_helper import normalize
from django.utils.http import (
    RFC3986_SUBDELIMS,
    escape_leading_slashes,
)


class RouteMatch(object):
    __slots__ = ('route', 'url_params')

    def __init__(self, route, url_params):
        self.route = route
        self.url_params = url_params


class Route(models.Model):
    order = models.IntegerField(null=True)
    name = models.TextField(null=False, blank=False)
    path = models.TextField(null=False, blank=False)
    endpoint = models.TextField(null=False, blank=False)
    template_name = models.TextField(null=False, blank=False)

    def match(self, path):
        m = re.match(_route_to_regex(self.path)[0], path)
        if m is None:
            return None
        return RouteMatch(self, m.groupdict())


def find_route(path):
    for route in Route.objects.order_by('order', 'path').all():
        m = route.match(path)
        if m is not None:
            return m
    else:
        return None


def reverse_route(route_name, args=None, kwargs=None):
    args = args or []
    kwargs = kwargs or {}
    prefix = get_script_prefix()

    try:
        route = Route.objects.filter(name=route_name).get()
    except Route.DoesNotExist:
        msg = (
            "Reverse for '%s' not found." % (route_name)
        )
        raise NoReverseMatch(msg)

    converters = _route_to_regex(route.path)[1]

    for result, params in normalize(_route_to_regex(route.path)[0]):
        if args:
            if len(args) != len(params):
                continue
            candidate_subs = dict(zip(params, args))
        else:
            if set(kwargs).symmetric_difference(params):
                continue
            candidate_subs = kwargs

        text_candidate_subs = {}
        for k, v in candidate_subs.items():
            if k in converters:
                text_candidate_subs[k] = converters[k].to_url(v)
            else:
                text_candidate_subs[k] = str(v)

        candidate_pat = prefix.replace('%', '%%') + result
        url = urllib.parse.quote(candidate_pat % text_candidate_subs, safe=RFC3986_SUBDELIMS + '/~:@')
        return escape_leading_slashes(url)

    if args:
        arg_msg = "arguments '%s'" % (args,)
    elif kwargs:
        arg_msg = "keyword arguments '%s'" % (kwargs,)
    else:
        arg_msg = "no arguments"
    msg = (
        "Reverse for '%s' with %s not matched." % (route_name, arg_msg)
    )
    raise NoReverseMatch(msg)
