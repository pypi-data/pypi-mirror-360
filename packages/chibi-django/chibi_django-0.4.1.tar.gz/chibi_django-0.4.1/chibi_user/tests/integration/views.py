from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from chibi_user.models import Token
from test_runners.simple_view import API_test_case
from chibi_user.tests import get_superuser_test
from test_runners.snippet.response import (
    get_location, assert_status_code
)
from test_runners.simple_view import Test_token_user
from django.contrib.auth import get_user_model

from faker import Factory as Faker_factory


fake = Faker_factory.create()


class Test_user( API_test_case ):
    namespace = 'users'
    name = 'users'

    def create_user( self, password='password' ):
        User_model = get_user_model()
        user = User_model.objects.create_user_test( password=password )
        return user

    @property
    def login( self ):
        url = self.reverse( 'login' )
        return url

    @property
    def me( self ):
        return reverse( 'users:me-me' )


class Test_views_normal_user( Test_token_user ):
    model = Token
    path = '/token/'
    namespace = 'users'
    name = 'users'

    @property
    def token_list( self ):
        url = self.reverse( 'tokens-list' )
        return url

    def test_fail_with_normal_user( self ):
        response = self.client.get( self.list )
        assert_status_code( response, status.HTTP_403_FORBIDDEN )


class Test_views_normal_user_2( Test_token_user, Test_user ):
    def test_me_should_work( self ):
        response = self.client.get( self.me )
        assert_status_code( response, status.HTTP_200_OK )


class Test_view_login( Test_user ):
    def test_get_method_should_no_be_allowed( self ):
        response = self.client.get( self.login )
        assert_status_code( response, status.HTTP_405_METHOD_NOT_ALLOWED )

    def test_login_should_return_the_token_key( self ):
        user = self.create_user( password='password' )
        response = self.client.post( self.login, data={
            'username': user.username,
            'password': 'password'
        } )
        assert_status_code( response, status.HTTP_200_OK )
        self.assertIn( 'key', response.data )
        self.assertIn( 'create_at', response.data )
        self.assertTrue( response.data[ 'key' ] )
        self.assertTrue( response.data[ 'create_at' ] )

    def test_login_key_should_work_like_authetication( self ):
        user = self.create_user( password='password' )
        response = self.client.post( self.login, data={
            'username': user.username,
            'password': 'password'
        } )
        assert_status_code( response, status.HTTP_200_OK )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {response.data[ 'key' ]}" )
        response = self.client.get( self.me )
        assert_status_code( response, status.HTTP_200_OK )

    def test_the_return_key_should_work_to_authenticate( self ):
        response = self.client.post( self.login )
        assert_status_code( response, status.HTTP_400_BAD_REQUEST )

    def test_password_and_user_is_required_data( self ):
        response = self.client.post( self.login )
        assert_status_code( response, status.HTTP_400_BAD_REQUEST )
        self.assertIn( 'password', response.data )
        self.assertIn( 'username', response.data )


class Test_views( API_test_case ):
    model = Token
    path = '/token/'

    def setUp( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        self.super_user, self.super_token = get_superuser_test()
        self.user, self.user_token = get_superuser_test()
        self.client.credentials( HTTP_AUTHORIZATION=str( self.user_token ) )

    def test_access_with_super_user( self ):
        auth = str( self.super_token )
        response = self.client.get( '/users/',
                                    HTTP_AUTHORIZATION=auth )

        self.assertEqual( response.status_code, status.HTTP_200_OK )

    def test_create_user( self ):
        auth = str( self.super_token )
        response = self.client.post(
            '/users/', HTTP_AUTHORIZATION=auth,
            data={
                'first_name': fake.first_name(),
                'last_name': fake.last_name(), 'email': fake.email(),
                'username': fake.user_name(),
            } )

        self.assertEqual( response.status_code, status.HTTP_201_CREATED,
                          ( "the status code should be 200 instead "
                            "of {}\ndata:{}" ).format( response.status_code,
                                                       response.data ) )
        assert_status_code( response, status.HTTP_201_CREATED )
        response = get_location( response, client=self.client )

        self.assertIsInstance( response.data[ 'pk' ], str )
        self.assertIn( 'token', response.data )
        self.assertIn( 'key', response.data[ 'token' ] )
        self.assertIsInstance( response.data[ 'token' ][ 'key' ], str )
        return response.data

    def test_delete_user( self ):
        data = self.test_create_user()
        auth = str( self.super_token )
        url = reverse( 'users:users-detail', kwargs={ 'pk': data[ 'pk' ] } )
        response = self.client.delete( url, HTTP_AUTHORIZATION=auth )

        self.assertEqual( response.status_code, status.HTTP_204_NO_CONTENT )

    def test_refresh_token( self ):
        data = self.test_create_user()
        auth = str( self.super_token )
        url = reverse(
            'users:users-refresh-token', kwargs={ 'pk': data[ 'pk' ] } )
        response = self.client.post( url, HTTP_AUTHORIZATION=auth )

        self.assertEqual( response.status_code, status.HTTP_200_OK )
        self.assertNotEqual( data[ 'token' ][ 'key' ],
                             response.data[ 'key' ] )
