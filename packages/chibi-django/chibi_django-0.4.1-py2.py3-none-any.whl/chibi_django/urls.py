from django.contrib import admin
from django.urls import path, include
from chibi_user import views as chibi_user_views
from chibi_user import urls as users_urls
from chibi_django.snippet.url import show_urls


urlpatterns = [
    path( '^$', chibi_user_views.index ),
    path( r'^dashboard', chibi_user_views.dashboard ),
    path(
        r'^', include(
            ( 'django.contrib.auth.urls', 'django_contrib' ),
            namespace='auth' ) ),
    path( 'admin/', admin.site.urls ),
    path( r'', include( ( users_urls, 'users' ), namespace='users' ), ),
]

show_urls( urlpatterns )
