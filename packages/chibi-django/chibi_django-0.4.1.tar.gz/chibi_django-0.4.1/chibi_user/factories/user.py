import factory
from factory import fuzzy
from faker import Factory as Faker_factory

from .token import Token
from django.contrib.auth import get_user_model
# from django.db.models import signals


User_model = get_user_model()
faker = Faker_factory.create()


# @factory.django.mute_signals( signals.post_save )
class User( factory.django.DjangoModelFactory ):
    username = factory.LazyAttribute( lambda x: faker.user_name() )
    is_active = fuzzy.FuzzyChoice( [ True, False ] )
    is_staff = fuzzy.FuzzyChoice( [ True, False ] )

    token = factory.RelatedFactory( Token, factory_related_name='user' )

    class Meta:
        model = User_model
