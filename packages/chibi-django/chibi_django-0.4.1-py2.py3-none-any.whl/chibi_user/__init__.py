from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


def get_token_model():
    """
    Return the User model that is active in this project.
    """
    try:
        return django_apps.get_model(
            settings.AUTH_TOKEN_MODEL, require_ready=False )
    except ValueError:
        raise ImproperlyConfigured(
            "AUTH_TOKEN_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_TOKEN_MODEL refers to model "
            "'%s' that has not been installed" % settings.AUTH_TOKEN_MODEL
        )


def get_group_model():
    """
    Return the Group model that is active in this project.
    """
    try:
        return django_apps.get_model(
            settings.AUTH_GROUP_MODEL, require_ready=False )
    except ValueError:
        raise ImproperlyConfigured(
            "AUTH_GROUP_MODEL must be of the form 'app_label.model_name'" )
    except LookupError:
        raise ImproperlyConfigured(
            f"AUTH_GROUP_MODEL refers to model "
            f"'{settings.AUTH_GROUP_MODEL}' that has not been installed"
        )


def get_permission_model():
    """
    Return the Permission model that is active in this project.
    """
    try:
        return django_apps.get_model(
            settings.AUTH_PERMISSION_MODEL, require_ready=False )
    except ValueError:
        raise ImproperlyConfigured(
            "AUTH_PERMISSION_MODEL must be of the "
            "form 'app_label.model_name'" )
    except LookupError:
        raise ImproperlyConfigured(
            f"AUTH_PERMISSION_MODEL refers to model "
            f"'{settings.AUTH_PERMISSION_MODEL}' that has not been installed"
        )
