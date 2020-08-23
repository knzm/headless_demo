from django.db import models
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now


# clone of dbtemplates.models.Template
class Template(models.Model):
    name = models.CharField(_('name'), max_length=100,
                            help_text=_("Example: 'flatpages/default.html'"))
    content = models.TextField(_('content'), blank=True)
    sites = models.ManyToManyField(Site, verbose_name=_(u'sites'), blank=True,
                                   related_name='custom_templates')
    creation_date = models.DateTimeField(_('creation date'), default=now)
    last_changed = models.DateTimeField(_('last changed'), default=now)
    published = models.BooleanField(null=True, default=False)

    objects = models.Manager()
    on_site = CurrentSiteManager('sites')

    class Meta:
        db_table = 'custom_dbtemplate'
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.last_changed = now()
        super(Template, self).save(*args, **kwargs)
