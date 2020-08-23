from django.conf import settings
from django.contrib.sites.models import Site
from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader

from reversion.models import Version

from .models import Template


class Loader(BaseLoader):
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        yield Origin(
            name=template_name,
            template_name=template_name,
            loader=self,
        )

    def get_contents(self, origin):
        content = self._load_template_source(origin.template_name)
        return content

    def _load_and_store_template(self, template_name, site, **params):
        if settings.ALLOW_PREVIEW:
            template = Template.objects.get(name__exact=template_name, **params)
            queryset = Version.objects.get_for_object(template)
            version = queryset.order_by('-pk')[:1].get()
            template = version._object_version.object
            return template.content

        else:
            queryset = Template.objects.filter(published=True)
            template = queryset.get(name__exact=template_name, **params)
            return template.content

    def _load_template_source(self, template_name, template_dirs=None):
        site = Site.objects.get_current()
        try:
            return self._load_and_store_template(
                template_name, site, sites__in=[site.id])
        except (Template.MultipleObjectsReturned, Template.DoesNotExist):
            pass
        try:
            return self._load_and_store_template(
                template_name, site, sites__isnull=True)
        except (Template.MultipleObjectsReturned, Template.DoesNotExist):
            pass

        raise TemplateDoesNotExist(template_name)
