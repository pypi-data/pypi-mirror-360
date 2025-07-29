from django.test import TestCase
from unittest.mock import patch
from chibi_user.models.user import User


class Test_user_manager( TestCase ):
    @patch( "chibi_user.models.User.save" )
    @patch( "chibi_user.models.User.refresh_token" )
    def test_create_user( self, token_save, user_save ):
        user = User.objects.create_user( username='test', password='password' )
        self.assertTrue( user_save.called )
        self.assertTrue( token_save.called )
        self.assertEqual( user.username, "test" )
        self.assertTrue( user.check_password( "password" ) )
        self.assertTrue( user.is_active )
        self.assertFalse( user.is_staff )

    @patch( "chibi_user.models.User.save" )
    @patch( "chibi_user.models.User.refresh_token" )
    def test_create_superuser( self, token_save, user_save ):
        user = User.objects.create_superuser(
            username='test', password='password' )
        self.assertTrue( user.is_staff )
        self.assertTrue( user.is_superuser )
        self.assertTrue( user_save.called )
        self.assertTrue( token_save.called )

    @patch( "chibi_user.models.User.save" )
    @patch( "chibi_user.models.User.refresh_token" )
    def test_create_superuser_test( self, token_save, user_save ):
        user = User.objects.create_superuser_test()
        self.assertTrue( user.is_staff )
        self.assertTrue( user.is_superuser )
        self.assertTrue( user_save.called )
        self.assertTrue( token_save.called )

    @patch( "chibi_user.models.User.save" )
    @patch( "chibi_user.models.User.refresh_token" )
    def test_create_user_test( self, token_save, user_save ):
        user = User.objects.create_user_test()
        self.assertFalse( user.is_staff )
        self.assertFalse( user.is_superuser )
        self.assertTrue( user_save.called )
        self.assertTrue( token_save.called )
