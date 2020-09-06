from django import template

from django.template.base import (
    Node,
    TemplateSyntaxError,
    kwarg_re,
)
from django.utils.html import conditional_escape

register = template.Library()


class RouteURLNode(Node):
    def __init__(self, route_name, args, kwargs, asvar):
        self.route_name = route_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        from django.urls import NoReverseMatch
        from ..models import reverse_route
        args = [arg.resolve(context) for arg in self.args]
        kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}
        route_name = self.route_name.resolve(context)
        try:
            url = reverse_route(route_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            if self.asvar is None:
                raise

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            if context.autoescape:
                url = conditional_escape(url)
            return url


@register.tag
def route_url(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument, a URL pattern name." % bits[0])
    route_name = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to url tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))

    return RouteURLNode(route_name, args, kwargs, asvar)
