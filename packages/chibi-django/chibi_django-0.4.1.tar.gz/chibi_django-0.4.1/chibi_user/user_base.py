from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from chibi_user.managers import User_manager
from chibi_user.models.mixin import Permissions_mixin
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


class Group_base( models.Model ):
    name = models.CharField( _( 'name' ), max_length=128, unique=True )
    permissions = models.ManyToManyField(
        settings.AUTH_PERMISSION_MODEL,
        verbose_name=_( 'permissions' ),
        blank=True,
    )

    class Meta:
        abstract = True
        verbose_name = _( 'group' )
        verbose_name_plural = _( 'groups' )

    def __str__( self ):
        return self.name

    def natural_key( self ):
        return ( self.name,)


class Permission_base( models.Model ):
    name = models.CharField( _( 'name' ), max_length=255 )
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        related_name='+',
        verbose_name=_( 'content type' ),
    )
    codename = models.CharField( _( 'codename' ), max_length=100 )

    class Meta:
        abstract = True
        verbose_name = _( 'permission' )
        verbose_name_plural = _( 'permissions' )
        unique_together = ( ('content_type', 'codename' ),)
        ordering = (
            'content_type__app_label', 'content_type__model', 'codename' )

    def __str__( self ):
        return f'{self.content_type} | {self.name}'

    def natural_key( self ):
        return ( self.codename, ) + self.content_type.natural_key()
    natural_key.dependencies = [ 'contenttypes.contenttype' ]


class User_base( AbstractBaseUser, Permissions_mixin ):
    """
    Modelo de usuarios para personalisar los campos
    """
    username_validator = UnicodeUsernameValidator()
    username = models.CharField( unique=True, max_length=64, )

    first_name = models.CharField(
        _('first name'), max_length=150, blank=True )
    last_name = models.CharField( _('last name' ), max_length=150, blank=True )
    email = models.EmailField( _( 'email address' ), blank=True )
    is_staff = models.BooleanField(
        _( 'staff status' ), default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.' ),
    )
    is_active = models.BooleanField(
        _( 'active' ), default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _( 'date joined' ), default=timezone.now )

    objects = User_manager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def __str__( self ):
        return "pk: {} :: username: {}".format( self.pk, self.username )

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        raise NotImplementedError( "implementar funcion para enviar correos" )
        # send_mail( subject, message, from_emai l, [ self.email ], **kwargs )

    def refresh_token( self, using=None ):
        """
        TODO: make test
        Refresca el token el usuario o lo crea

        Returns
        -------

        Token
            token que se genero para el usuario
        """
        from chibi_user.models.token import Token
        try:
            if self.token:
                self.token.delete()
        except Token.DoesNotExist:
            pass
        finally:
            token = Token.objects.create( user=self, )
            return token
