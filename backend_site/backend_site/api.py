from rest_framework.response import Response
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from wagtail.core.models import Page, Site


class DraftPagesAPIViewSet(PagesAPIViewSet):
    known_query_parameters = \
        PagesAPIViewSet.known_query_parameters.union(['draft'])

    def include_draft(self):
        return self.request.GET.get('draft')

    def get_base_queryset(self):
        if not self.include_draft():
            return super(DraftPagesAPIViewSet, self).get_base_queryset()

        site = Site.find_for_request(self.request)
        if not site:
            return super(DraftPagesAPIViewSet, self).get_base_queryset()

        queryset = Page.objects.all()
        queryset = queryset.descendant_of(site.root_page, inclusive=True)
        return queryset

    def listing_view(self, request):
        if not self.include_draft():
            return super(DraftPagesAPIViewSet, self).listing_view(request)

        queryset = self.get_queryset()
        self.check_query_parameters(queryset)
        queryset = self.filter_queryset(queryset)
        queryset = self.paginate_queryset(queryset)
        instances = [instance.get_latest_revision_as_page()
                     for instance in queryset]
        serializer = self.get_serializer(instances, many=True)
        return self.get_paginated_response(serializer.data)

    def detail_view(self, request, pk):
        if not self.include_draft():
            return super(DraftPagesAPIViewSet, self).detail_view(request, pk)
        instance = self.get_object().get_latest_revision_as_page()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DraftBlogPagesAPIViewSet(DraftPagesAPIViewSet):
    listing_default_fields = ['id', 'type', 'detail_url', 'body']

    def get_queryset(self):
        from backend_site.blog.models import BlogPage
        return BlogPage.objects.filter(
            id__in=self.get_base_queryset().values_list('id', flat=True)
        )


# Create the router. "wagtailapi" is the URL namespace
api_router = WagtailAPIRouter('wagtailapi')

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
api_router.register_endpoint('pages', DraftPagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)
api_router.register_endpoint('blogs', DraftBlogPagesAPIViewSet)
