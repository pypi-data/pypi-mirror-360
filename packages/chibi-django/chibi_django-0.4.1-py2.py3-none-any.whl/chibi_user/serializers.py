from rest_framework import serializers
from chibi_user.models import Token as Token_model
from chibi_django.serializers_fields import (
    parametrise_hyperlink_identity_field
)

from django.contrib.auth import get_user_model
User_model = get_user_model()


class Token( serializers.ModelSerializer ):
    class Meta:
        model = Token_model
        fields = [ 'key', 'create_at' ]


class User( serializers.ModelSerializer ):
    token = Token( required=False )

    class Meta:
        model = User_model
        fields = [ 'pk', 'is_active', 'token' ]
        read_only_fields = [ 'pk', 'is_active', 'token' ]


class User_create( serializers.ModelSerializer ):
    url = parametrise_hyperlink_identity_field(
        lookup_obj_fields=( ( 'pk', 'pk', ), ),
        view_name='users:users-detail' )

    class Meta:
        model = User_model
        fields = [
            'pk', 'url', 'first_name', 'last_name', 'username', 'is_staff',
            'email', 'is_superuser', 'is_active' ]
        read_only_fields = [ 'pk', 'url' ]

    def create( self, validate_data ):
        user = User_model.objects.create( **validate_data )
        return user


class Login( serializers.ModelSerializer ):

    username = serializers.CharField( allow_blank=True, required=True )

    class Meta:
        model = User_model
        fields = [ 'username', 'password' ]
        # read_only_fields = [ 'pk', 'is_active', 'token' ]


class Me( serializers.ModelSerializer ):
    class Meta:
        model = User_model
        fields = [
            'pk', 'username', 'first_name', 'last_name', 'email', 'is_active' ]
        read_only_fields = [ 'pk', 'is_active'  ]
