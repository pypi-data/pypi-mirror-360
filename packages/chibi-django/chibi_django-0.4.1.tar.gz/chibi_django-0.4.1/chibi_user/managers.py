from chibi import madness
from django.apps import apps
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.db import models


class User_manager( BaseUserManager ):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError( 'The given username must be set' )
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name )
        username = GlobalUserModel.normalize_username( username )
        user = self.model( username=username, email=email, **extra_fields )
        user.password = make_password( password )
        user.save( using=self._db )
        user.refresh_token( using=self._db )
        return user

    def create_superuser(
            self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def with_perm(
            self, perm, is_active=True, include_superusers=True,
            backend=None, obj=None ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create( self, *args, password='', **kw ):
        user = super().create( *args, password=password, **kw )
        user.set_password( password )
        user.save()
        user.refresh_token()
        return user

    def create_user_test( self, *args, username=None, password=None, **kw ):
        """
        Crea un usuario para pruebas
        """
        if not username:
            username = madness.string.generate_string()
        if not password:
            password = 'password'
        user = self.create_user(
            *args, username=username, password=password, **kw )
        return user

    def create_superuser_test(
            self, *args, username=None, password=None, **kw ):
        """
        Crea un super usuairo para las pruebas
        """
        if not username:
            username = madness.string.generate_string()
        if not password:
            password = 'password'
        user = self.create_superuser(
            *args, username=username, password=password, **kw )
        return user

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit( '@', 1 )
        except ValueError:
            pass
        else:
            email = email_name + '@' + domain_part.lower()
        return email

    def make_random_password(
            self, length=10,
            allowed_chars=(
                'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
                '123456789' ) ):
        """
        Generate a random password with the given length and given
        allowed_chars. The default value of allowed_chars does not have "I" or
        "O" or letters and digits that look similar -- just to avoid confusion.
        """
        raise NotImplementedError( "implementar funcion get_random_string" )
        # return get_random_string( length, allowed_chars )

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


class Permission_manager( models.Manager ):
    use_in_migrations = True

    def get_by_natural_key( self, codename, app_label, model ):
        return self.get(
            codename=codename,
            content_type=(
                ContentType.objects.db_manager(
                    self.db ).get_by_natural_key( app_label, model ),
            ) )


class Group_manager( models.Manager ):
    use_in_migrations = True

    def get_by_natural_key( self, name ):
        return self.get( name=name )
