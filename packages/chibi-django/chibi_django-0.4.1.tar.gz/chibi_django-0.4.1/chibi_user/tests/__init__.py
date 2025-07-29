from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework_nested import routers

try:
    from chibi_user.models import Token as Token_model
except Exception:
    pass

from django.contrib.auth import get_user_model


factory = APIRequestFactory()


def get_superuser_test():
    User_model = get_user_model()
    try:
        user = User_model.objects.filter( is_staff=True )[0]
    except Exception:
        user = User_model.objects.create_superuser_test()
    try:
        token = user.token
    except Token_model.DoesNotExist:
        token = user.refresh_token()
    return user, token


def get_user_test( pk=None ):
    User_model = get_user_model()
    try:
        user = User_model.objects.filter( is_staff=False )[0]
    except Exception:
        user = User_model.objects.create_user_test( pk=pk )
    try:
        token = user.token
    except Token_model.DoesNotExist:
        token = user.refresh_token()
    return user, token


class Mock_View_authenticated( viewsets.ViewSet ):
    permission_classes = ( permissions.IsAuthenticated, )

    def list( self, request, format=None ):
        return Response(
            { 'a': 1, 'b': 2, 'c': 3 }, status=status.HTTP_200_OK )

    def retrieve( self, request, pk, format=None ):
        return Response(
            { 'a': 1, 'b': 2, 'c': 3 }, status=status.HTTP_200_OK )

    def update( self, request, pk, format=None ):
        return Response(
            { 'a': 1, 'b': 2, 'c': 3 }, status=status.HTTP_200_OK )

    def create( self, request, format=None ):
        return Response(
            { 'a': 1, 'b': 2, 'c': 3 }, status=status.HTTP_200_OK )


class Mock_view_all_404( viewsets.ViewSet ):
    permission_classes = ( permissions.IsAuthenticated, )

    def list( self, request, format=None ):
        return Response( {}, status=status.HTTP_404_NOT_FOUND )

    def retrieve( self, request, pk, format=None ):
        return Response( {}, status=status.HTTP_404_NOT_FOUND )

    def update( self, request, pk, format=None ):
        return Response( {}, status=status.HTTP_404_NOT_FOUND )


router = routers.SimpleRouter()
router.register( r'token', Mock_View_authenticated, basename='token' )
router.register( r'fail_soft', Mock_view_all_404, basename='fail_soft' )

urlpatterns = router.urls
