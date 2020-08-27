import datetime

from django.test import TestCase
from django.test import override_settings
from django.http.request import HttpRequest
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone
from django.utils.formats import localize
from django.utils.timezone import template_localtime
from django.utils.functional import cached_property

import reversion
from reversion.models import Revision, Version

from frontend_site.custom_dbtemplates.models import Template
from frontend_site.custom_dbtemplates.admin import CustomTemplateAdmin


class CustomTemplateAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.user = User()
        self.user.is_superuser = True
        self.user.save()

    @cached_property
    def changelist_url(self):
        opts = Template._meta
        return reverse(f'admin:{opts.app_label}_{opts.model_name}_changelist')

    def get_model_admin(self):
        return CustomTemplateAdmin(Template, self.site)

    def get_request(self):
        request = HttpRequest()
        request.META['SCRIPT_NAME'] = ''
        request.user = self.user
        request.session = 'session'
        request._dont_enforce_csrf_checks = True
        request._messages = FallbackStorage(request)
        return request

    def test_add_new(self):
        admin = self.get_model_admin()
        request = self.get_request()
        request.method = 'POST'
        request.POST = {
            'name': 'test.html',
            'content': 'test',
            'creation_date_0': '2020-01-01',
            'creation_date_1': '00:00:00',
            'last_changed_0': '2020-01-01',
            'last_changed_1': '00:00:00',
            '_save': 'Save',
        }
        response = admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), self.changelist_url)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Revision.objects.count(), 1)
        self.assertEqual(Version.objects.count(), 1)
        obj = Template.objects.get()
        revision = Revision.objects.get()
        version = Version.objects.get()
        self.assertFalse(obj.published)
        self.assertEqual(revision.comment, 'Added.')
        self.assertEqual(version._object_version.object.content, obj.content)

    def test_add_new_and_publish(self):
        admin = self.get_model_admin()
        request = self.get_request()
        request.method = 'POST'
        request.POST = {
            'name': 'test.html',
            'content': 'test',
            'creation_date_0': '2020-01-01',
            'creation_date_1': '00:00:00',
            'last_changed_0': '2020-01-01',
            'last_changed_1': '00:00:00',
            '_publish': 'Save and publish',
        }
        response = admin.add_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), self.changelist_url)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Revision.objects.count(), 1)
        self.assertEqual(Version.objects.count(), 1)
        obj = Template.objects.get()
        revision = Revision.objects.get()
        version = Version.objects.get()
        self.assertTrue(obj.published)
        self.assertEqual(revision.comment, 'Added.')
        self.assertEqual(version._object_version.object.content, obj.content)
        self.assertFalse(version._object_version.object.published)

    def test_update_draft(self):
        tz = timezone.make_aware(datetime.datetime(2020, 1, 1))
        with reversion.revisions.create_revision(manage_manually=True):
            obj = Template(
                name='test.html',
                content='test',
                creation_date=tz,
                last_changed=tz,
                published=False,
            )
            obj.save()
            reversion.revisions.add_to_revision(obj)
            reversion.revisions.set_comment("Draft")

        admin = self.get_model_admin()
        request = self.get_request()
        request.method = 'POST'
        request.POST = {
            'name': 'test.html',
            'content': 'test 2',
            'creation_date_0': '2020-01-01',
            'creation_date_1': '00:00:00',
            'last_changed_0': '2020-01-01',
            'last_changed_1': '00:00:00',
            '_save': 'Save',
        }
        response = admin.change_view(request, str(obj.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), self.changelist_url)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Revision.objects.count(), 2)
        self.assertEqual(Version.objects.count(), 2)
        obj = Template.objects.get()
        self.assertFalse(obj.published)
        revisions = Revision.objects.order_by('id').all()
        versions = Version.objects.order_by('id').all()
        for revision, version in zip(revisions, versions):
            self.assertEqual(version.revision_id, revision.id)
        deserialized_objs = [
            version._object_version.object
            for version in versions
        ]
        self.assertEqual([revision.comment for revision in revisions],
                         ['Draft', 'Draft'])
        self.assertEqual([obj.content for obj in deserialized_objs],
                         ['test', 'test 2'])
        self.assertEqual([obj.published for obj in deserialized_objs],
                         [False] * 2)

    def test_update_draft_and_publish(self):
        tz = timezone.make_aware(datetime.datetime(2020, 1, 1))
        with reversion.revisions.create_revision(manage_manually=True):
            obj = Template(
                name='test.html',
                content='test',
                creation_date=tz,
                last_changed=tz,
                published=False,
            )
            obj.save()
            reversion.revisions.add_to_revision(obj)
            reversion.revisions.set_comment("Draft")

        admin = self.get_model_admin()
        request = self.get_request()
        request.method = 'POST'
        request.POST = {
            'name': 'test.html',
            'content': 'test 2',
            'creation_date_0': '2020-01-01',
            'creation_date_1': '00:00:00',
            'last_changed_0': '2020-01-01',
            'last_changed_1': '00:00:00',
            '_publish': 'Save and publish',
        }
        response = admin.change_view(request, str(obj.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), self.changelist_url)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Revision.objects.count(), 2)
        self.assertEqual(Version.objects.count(), 2)
        obj = Template.objects.get()
        self.assertTrue(obj.published)
        revisions = Revision.objects.order_by('id').all()
        versions = Version.objects.order_by('id').all()
        for revision, version in zip(revisions, versions):
            self.assertEqual(version.revision_id, revision.id)
        deserialized_objs = [
            version._object_version.object
            for version in versions
        ]
        self.assertEqual([revision.comment for revision in revisions],
                         ['Draft', 'Publish.'])
        self.assertEqual([obj.content for obj in deserialized_objs],
                         ['test', 'test 2'])
        self.assertEqual([obj.published for obj in deserialized_objs],
                         [False] * 2)

    def test_update_public(self):
        tz = timezone.make_aware(datetime.datetime(2020, 1, 1))
        with reversion.revisions.create_revision(manage_manually=True):
            obj = Template(
                name='test.html',
                content='test',
                creation_date=tz,
                last_changed=tz,
                published=True,
            )
            obj.save()
            obj.published = False
            reversion.revisions.add_to_revision(obj)
            reversion.revisions.set_comment("Publish.")

        admin = self.get_model_admin()
        request = self.get_request()
        request.method = 'POST'
        request.POST = {
            'name': 'test.html',
            'content': 'test 2',
            'creation_date_0': '2020-01-01',
            'creation_date_1': '00:00:00',
            'last_changed_0': '2020-01-01',
            'last_changed_1': '00:00:00',
            '_save': 'Save',
        }
        response = admin.change_view(request, str(obj.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), self.changelist_url)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Revision.objects.count(), 2)
        self.assertEqual(Version.objects.count(), 2)
        obj = Template.objects.get()
        self.assertFalse(obj.published)
        revisions = Revision.objects.order_by('id').all()
        versions = Version.objects.order_by('id').all()
        for revision, version in zip(revisions, versions):
            self.assertEqual(version.revision_id, revision.id)
        deserialized_objs = [
            version._object_version.object
            for version in versions
        ]
        self.assertEqual([revision.comment for revision in revisions],
                         ['Publish.', 'Draft'])
        self.assertEqual([obj.content for obj in deserialized_objs],
                         ['test', 'test 2'])
        self.assertEqual([obj.published for obj in deserialized_objs],
                         [False] * 2)

    def test_update_public_and_publish(self):
        tz = timezone.make_aware(datetime.datetime(2020, 1, 1))
        with reversion.revisions.create_revision(manage_manually=True):
            obj = Template(
                name='test.html',
                content='test',
                creation_date=tz,
                last_changed=tz,
                published=True,
            )
            obj.save()
            obj.published = False
            reversion.revisions.add_to_revision(obj)
            reversion.revisions.set_comment("Publish.")

        admin = self.get_model_admin()
        request = self.get_request()
        request.method = 'POST'
        request.POST = {
            'name': 'test.html',
            'content': 'test 2',
            'creation_date_0': '2020-01-01',
            'creation_date_1': '00:00:00',
            'last_changed_0': '2020-01-01',
            'last_changed_1': '00:00:00',
            '_publish': 'Save and publish',
        }
        response = admin.change_view(request, str(obj.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), self.changelist_url)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Revision.objects.count(), 2)
        self.assertEqual(Version.objects.count(), 2)
        obj = Template.objects.get()
        self.assertTrue(obj.published)
        revisions = Revision.objects.order_by('id').all()
        versions = Version.objects.order_by('id').all()
        for revision, version in zip(revisions, versions):
            self.assertEqual(version.revision_id, revision.id)
        deserialized_objs = [
            version._object_version.object
            for version in versions
        ]
        self.assertEqual([revision.comment for revision in revisions],
                         ['Publish.', 'Publish.'])
        self.assertEqual([obj.content for obj in deserialized_objs],
                         ['test', 'test 2'])
        self.assertEqual([obj.published for obj in deserialized_objs],
                         [False] * 2)

    def test_revert_draft(self):
        tz = timezone.make_aware(datetime.datetime(2020, 1, 1))
        with reversion.revisions.create_revision(manage_manually=True):
            obj = Template(
                name='test.html',
                content='test',
                creation_date=tz,
                last_changed=tz,
                published=False,
            )
            obj.save()
            reversion.revisions.add_to_revision(obj)
            reversion.revisions.set_comment("Draft")

        with reversion.revisions.create_revision(manage_manually=True):
            obj.content = 'test 2'
            obj.save()
            reversion.revisions.add_to_revision(obj)
            reversion.revisions.set_comment("Draft")

        versions = Version.objects.order_by('id').all()
        self.assertEqual(len(versions), 2)

        admin = self.get_model_admin()
        request = self.get_request()
        request.method = 'POST'
        request.POST = {
            'name': 'test.html',
            'content': 'test',
            'creation_date_0': '2020-01-01',
            'creation_date_1': '00:00:00',
            'last_changed_0': '2020-01-01',
            'last_changed_1': '00:00:00',
            '_save': 'Save',
        }
        response = admin.revision_view(request, str(obj.id), str(versions[0].id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), self.changelist_url)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Revision.objects.count(), 3)
        self.assertEqual(Version.objects.count(), 3)
        obj = Template.objects.get()
        self.assertFalse(obj.published)
        revisions = Revision.objects.order_by('id').all()
        versions = Version.objects.order_by('id').all()
        for revision, version in zip(revisions, versions):
            self.assertEqual(version.revision_id, revision.id)
        deserialized_objs = [
            version._object_version.object
            for version in versions
        ]
        revert_comment = 'Draft: Reverted to previous version, saved on %(datetime)s' % {
            'datetime': localize(template_localtime(list(revisions)[-1].date_created)),
        }
        self.assertEqual([revision.comment for revision in revisions],
                         ['Draft', 'Draft', revert_comment])
        self.assertEqual([obj.content for obj in deserialized_objs],
                         ['test', 'test 2', 'test'])
        self.assertEqual([obj.published for obj in deserialized_objs],
                         [False] * 3)

    @override_settings(DEBUG=True)
    def test_revert_editing(self):
        tz = timezone.make_aware(datetime.datetime(2020, 1, 1))
        with reversion.revisions.create_revision(manage_manually=True):
            obj = Template(
                name='test.html',
                content='test',
                creation_date=tz,
                last_changed=tz,
                published=True,
            )
            obj.save()
            obj.published = False
            reversion.revisions.add_to_revision(obj)
            reversion.revisions.set_comment("Publish.")

        with reversion.revisions.create_revision(manage_manually=True):
            obj.content = 'test 2'
            reversion.revisions.add_to_revision(obj)
            reversion.revisions.set_comment("Draft")

        versions = Version.objects.order_by('id').all()
        self.assertEqual(len(versions), 2)

        admin = self.get_model_admin()
        request = self.get_request()
        request.method = 'POST'
        request.POST = {
            'name': 'test.html',
            'content': 'test',
            'creation_date_0': '2020-01-01',
            'creation_date_1': '00:00:00',
            'last_changed_0': '2020-01-01',
            'last_changed_1': '00:00:00',
            '_publish': 'Save and publish',
        }
        response = admin.revision_view(request, str(obj.id), str(versions[0].id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), self.changelist_url)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Revision.objects.count(), 3)
        self.assertEqual(Version.objects.count(), 3)
        obj = Template.objects.get()
        self.assertTrue(obj.published)
        revisions = Revision.objects.order_by('id').all()
        versions = Version.objects.order_by('id').all()
        for revision, version in zip(revisions, versions):
            self.assertEqual(version.revision_id, revision.id)
        deserialized_objs = [
            version._object_version.object
            for version in versions
        ]
        revert_comment = 'Reverted to previous version, saved on %(datetime)s' % {
            'datetime': localize(template_localtime(list(revisions)[-1].date_created)),
        }
        self.assertEqual([revision.comment for revision in revisions],
                         ['Publish.', 'Draft', revert_comment])
        self.assertEqual([obj.content for obj in deserialized_objs],
                         ['test', 'test 2', 'test'])
        self.assertEqual([obj.published for obj in deserialized_objs],
                         [False] * 3)
