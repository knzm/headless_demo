from django import forms
from django.contrib import admin
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

import reversion
from reversion.models import Version
from reversion.revisions import create_revision

try:
    from reversion_compare.admin import CompareVersionAdmin as TemplateModelAdmin
except ImportError:
    try:
        from reversion.admin import VersionAdmin as TemplateModelAdmin
    except ImportError:
        from django.contrib.admin import ModelAdmin as TemplateModelAdmin

from .models import Template
from .fields import TemplateContentTextArea


class TemplateAdminForm(forms.ModelForm):
    """
    Custom AdminForm to make the content textarea wider.
    """
    content = forms.CharField(
        widget=TemplateContentTextArea(attrs={'rows': '24'}),
        required=False,
    )

    class Meta:
        model = Template
        fields = ('name', 'content', 'creation_date', 'last_changed')
        fields = "__all__"


class CustomTemplateAdmin(TemplateModelAdmin):
    form = TemplateAdminForm

    fieldsets = (
        (None, {
            'fields': ('name', 'content'),
            'classes': ('monospace',),
        }),
        (_('Date/time'), {
            'fields': (('creation_date', 'last_changed'),),
            'classes': ('collapse',),
        }),
    )
    list_display = ('name', 'creation_date', 'last_changed')
    save_as = True
    search_fields = ('name', 'content')

    # override: django.contrib.admin.options.ModelAdmin
    def save_model(self, request, obj, form, change):
        if obj.pk is None:
            obj.save()
        obj.published = False
        reversion.revisions.add_to_revision(obj)
        if '_publish' in form.data:
            obj.published = True
            obj.save()

    # override reversion.admin.VersionAdmin
    def add_view(self, request, form_url='', extra_context=None):
        with create_revision(manage_manually=True):
            return self.changeform_view(request, None, form_url, extra_context)

    # override reversion.admin.VersionAdmin
    def change_view(self, request, object_id, extra_context=None):
        queryset = Version.objects \
            .get_for_object_reference(self.model, object_id) \
            .select_related('revision')
        version = get_object_or_404(queryset.order_by('-pk')[:1])
        return self._dbtemplates_revisionform_view(
            request, version, template_name='', is_revert=False,
            extra_context=extra_context)

    # override reversion.admin.VersionAdmin
    def _reversion_revisionform_view(self, request, version, template_name, extra_context=None):
        return self._dbtemplates_revisionform_view(
            request, version, template_name, is_revert=True,
            extra_context=extra_context)

    def _get_comment(self, request, version, is_revert):
        from django.utils.formats import localize
        from django.utils.timezone import template_localtime
        if is_revert:
            return _("Reverted to previous version, saved on %(datetime)s") % {
                "datetime": localize(template_localtime(version.revision.date_created)),
            }
        elif '_publish' in request.POST:
            return _("Publish.")
        else:
            return _('Draft')

    # clone of VersionAdmin._reversion_revisionform_view
    def _dbtemplates_revisionform_view(self, request, version, template_name='', is_revert=False, extra_context=None):
        from django.db import models, connection
        from django.contrib import messages
        from django.contrib.admin.utils import quote
        from django.core.exceptions import ImproperlyConfigured
        from django.shortcuts import redirect
        from django.utils.encoding import force_str
        from reversion.errors import RevertError
        from reversion.views import _RollBackRevisionView

        # Check that database transactions are supported.
        if not connection.features.uses_savepoints:
            raise ImproperlyConfigured("Cannot use VersionAdmin with a database that does not support savepoints.")
        # Run the view.
        try:
            with transaction.atomic(using=version.db):
                # Revert the revision.
                version.revision.revert(delete=True)
                # Run the normal changeform view.
                with create_revision(manage_manually=True):
                    context = {
                        'show_publish_button': True,
                    }
                    if extra_context is not None:
                        context.update(extra_context)
                    response = self.changeform_view(request, quote(version.object_id), request.path, context)
                    # Decide on whether the keep the changes.
                    if request.method == "POST" and response.status_code == 302:
                        comment = self._get_comment(request, version, is_revert)
                        reversion.revisions.set_comment(comment)
                    else:
                        if template_name != '':
                            response.template_name = template_name  # Set the template name to the correct template.
                        if hasattr('response', 'render'):
                            response.render()  # Eagerly render the response, so it's using the latest version.
                        raise _RollBackRevisionView(response)  # Raise exception to undo the transaction and revision.
        except (RevertError, models.ProtectedError) as ex:
            opts = self.model._meta
            messages.error(request, force_str(ex))
            return redirect("{}:{}_{}_changelist".format(self.admin_site.name, opts.app_label, opts.model_name))
        except _RollBackRevisionView as ex:
            return ex.response
        return response


admin.site.register(Template, CustomTemplateAdmin)
