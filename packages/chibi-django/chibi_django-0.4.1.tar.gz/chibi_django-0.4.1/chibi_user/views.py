import json
from .models import Token as Token_model
from .serializers import (
    User as User_serializer, Token as Token_serializer,
    User_create as User_create_serializer
)
from .authentication import Token_simple_authentication
from chibi_django import view_set
from chibi_user.serializers import (
    Login as Login_serializer, Me as Me_serializer
)
from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required


User_model = get_user_model()


def index( request ):
    return render( request, 'index.html' )


@login_required
def dashboard( request ):
    user = request.user
    auth0user = user.social_auth.get( provider="auth0")
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture']
    }

    return render(
        request, 'dashboard.html',
        {
            'auth0User': auth0user,
            'userdata': json.dumps( userdata, indent=4 )
        } )


class User( view_set.Model_viewset ):
    authentication_classes = [ Token_simple_authentication ]
    permission_classes = [ IsAdminUser ]
    queryset = User_model.objects.all()
    filter_backends = ( filters.OrderingFilter, )
    ordering_fields = ( 'username', 'email' )
    ordering = ( 'username', )
    serializer_class = {
        'default': User_serializer,
        'create': User_create_serializer,
    }

    @action( detail=True, methods=[ 'POST' ] )
    def refresh_token( self, request, pk, format=None ):
        user = User_model.objects.get( pk=pk )
        token = user.refresh_token()
        serializer = Token_serializer( token )
        return Response( serializer.data )

    @action(
        detail=False, methods=[ 'POST' ],
        permission_classes=[ AllowAny ],
        authentication_classes=[]
    )
    def login( self, request, format=None, ):
        serializer = Login_serializer( data=request.data )
        serializer.is_valid( raise_exception=True )
        try:
            user = User_model.objects.get(
                username=serializer.data[ 'username' ] )
        except User_model.DoesNotExist:
            return Response( status=status.HTTP_403_FORBIDDEN )
        if user.check_password( serializer.data[ 'password' ] ):
            token = user.refresh_token()
            serializer = Token_serializer( token )
            return Response( serializer.data )
        else:
            return Response( status=status.HTTP_403_FORBIDDEN )


class Token( view_set.Model_viewset ):
    authentication_classes = [ Token_simple_authentication ]
    permission_classes = [ IsAdminUser ]
    # queryset               = Token_model.objects.all()
    serializer_class = Token_serializer

    def get_queryset( self, *args, **kw ):
        user_pk = self.kwargs[ 'users_pk' ]
        return Token_model.objects.filter( user__pk=user_pk )


class Login( viewsets.GenericViewSet ):
    authentication_classes = []
    permission_classes = [ AllowAny ]

    @action( detail=False, methods=[ 'POST' ] )
    def login( self, request, format=None ):
        serializer = Login_serializer( data=request.data )
        serializer.is_valid( raise_exception=True )
        try:
            user = User_model.objects.get(
                username=serializer.data[ 'username' ] )
        except User_model.DoesNotExist:
            return Response( status=status.HTTP_403_FORBIDDEN)
        if user.check_password( serializer.data[ 'password' ] ):
            token = user.refresh_token()
            serializer = Token_serializer( token )
            return Response( serializer.data )
        else:
            return Response( status=status.HTTP_403_FORBIDDEN)


class Me( viewsets.GenericViewSet ):
    # authentication_classes = [ Token_simple_authentication ]
    permission_classes = [ IsAuthenticated ]
    serializer_class = Me_serializer

    @action( detail=False, methods=[ 'GET' ] )
    def me( self, request, format=None ):
        serializer = Me_serializer( request.user )
        return Response( serializer.data )
