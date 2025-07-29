from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from .snippet.response import get_location
from chibi_user.tests import get_superuser_test, get_user_test
from django.db import models


class API_test_case( APITestCase ):
    namespace = None
    name = None

    def reverse( self, action, *args, **kw ):
        if not self.namespace:
            raise ValueError( f"no se asigno {type(self)}.namespace" )
        if not self.name:
            raise ValueError( f"no se asigno {type(self)}.name" )

        if action is None:
            return reverse(
                f'{self.namespace}:{self.name}', *args, **kw )

        return reverse(
            f'{self.namespace}:{self.name}-{action}', *args, **kw )

    @property
    def list( self ):
        url = self.reverse( 'list' )
        return url

    @property
    def detail( self ):
        url = self.reverse( 'detail' )
        return url

    def list_of( self, pk, lookup='pk' ):
        if isinstance( pk, models.Model ):
            pk = pk.pk
        return self.reverse( 'list', kwargs={ lookup: pk } )

    def detail_of( self, pk, lookup='pk', kwargs=None ):
        if isinstance( pk, models.Model ):
            pk = pk.pk
        if kwargs is None:
            kwargs = { lookup: pk }
        else:
            kwargs[ lookup ] = pk
        return self.reverse( 'detail', kwargs=kwargs )

    def get_location( self, response ):
        return get_location( response, client=self.client )

    def get_list( self, *args, **kw ):
        return self.client.get( self.list, *args, **kw )

    def get_detail_of( self, pk, lookup='pk', kwargs=None ):
        url = self.detail_of( pk, lookup=lookup, kwargs=kwargs )
        return self.client.get( url )


class Test_token_user( API_test_case ):

    def setUp( self ):
        super().setUp()
        self.password = 'password'
        self.client = self.client_class( enforce_csrf_checks=True )
        self.user, self.token = get_user_test()
        self.client.credentials( HTTP_AUTHORIZATION=str( self.token ) )


class Test_token_superuser( API_test_case ):

    def setUp( self ):
        super().setUp()
        self.password = 'password'
        self.client = self.client_class( enforce_csrf_checks=True )
        self.user, self.token = get_superuser_test()
        self.client.credentials( HTTP_AUTHORIZATION=str( self.token ) )
