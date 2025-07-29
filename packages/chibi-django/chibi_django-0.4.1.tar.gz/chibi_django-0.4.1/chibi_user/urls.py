from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()

router.register( r'', views.Me, basename='me' )
router.register( r'users', views.User, basename='users' )

token_router = routers.NestedSimpleRouter( router, r'users', lookup='users' )
token_router.register( r'token', views.Token, basename='tokens' )
token_router.register( r'login', views.Login, basename='login' )


urlpatterns = router.urls + token_router.urls
