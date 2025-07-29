import logging
from django.utils.translation import gettext as _
from chibi_django import mixins
from rest_framework import viewsets

from django.core.exceptions import ValidationError
from django.http import Http404
# from django.shortcuts import get_object_or_404 as _get_object_or_404

from elasticsearch.exceptions import NotFoundError


logger = logging.getLogger( 'chibi_django.exceptions' )


def get_object_or_404( queryset, *filter_args, **filter_kwargs ):
    try:
        index = queryset.index()
        if len( index._doc_type ) > 1:
            logger.warning( f'se encontro mas de un modelo {index._doc_type}' )
        return index._doc_type[0].get( filter_kwargs[ 'pk' ] )
    except ( TypeError, ValueError, ValidationError, NotFoundError ):
        raise Http404


class Multi_permission_viewset( viewsets.GenericViewSet ):
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this
         view requires.
        """
        if self.action is None:
            return [permission() for permission in self.permission_classes]
        func = getattr( self, self.action )
        if hasattr( func, 'permission_classes' ):
            return [ permission() for permission in func.permission_classes ]
        return [permission() for permission in self.permission_classes]


class Multi_serializer_viewset( Multi_permission_viewset ):
    def get_serializer( self, *args, serializer_name='default', **kw ):
        serializer_class = self.get_serializer_class( serializer_name )
        kw[ 'context' ] = self.get_serializer_context()
        return serializer_class( *args, **kw )

    def get_serializer_class( self, serializer_name='default' ):
        serializers = super().get_serializer_class()
        if not isinstance( serializers, dict ):
            return serializers
        try:
            serializer_class = serializers[ serializer_name ]
        except KeyError:
            try:
                serializer_class = serializers[ 'default' ]
            except KeyError:
                raise KeyError( _(
                    'The serializer %s is not defined' ) % serializer_name )
        return serializer_class


class Nested_view_set( Multi_serializer_viewset ):
    def create_build_data( self, data ):
        return data

    def update_build_data( self, data ):
        return data


class Elastic_view_set( Nested_view_set ):
    def get_object( self ):
        queryset = self.filter_queryset( self.get_queryset() )

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            ( self.__class__.__name__, lookup_url_kwarg )
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404( queryset, **filter_kwargs )

        # May raise a permission denied
        # self.check_object_permissions( self.request, obj )

        return obj


class Model_viewset(
        mixins.Create_model, mixins.Retrieve_model, mixins.Update_model,
        mixins.Destroy_model, mixins.List_model, Nested_view_set ):
    pass


class Elastic_model_viewset(
        mixins.Elastic_list_model, mixins.Elastic_retrieve_model,
        mixins.Elastic_create_model, Elastic_view_set ):
    pass


class Read_only_model_viewset(
        mixins.Retrieve_model, mixins.List_model, Nested_view_set ):
    pass


class List_only_model_viewset(
        mixins.List_model, Nested_view_set ):
    pass
