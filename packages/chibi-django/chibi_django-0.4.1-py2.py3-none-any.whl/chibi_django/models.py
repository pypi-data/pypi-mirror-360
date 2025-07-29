import datetime
import json
import logging

from chibi import madness
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from elasticsearch_dsl import Document, field


logger = logging.getLogger( 'chibi_django.models' )


class Chibi_model( models.Model ):
    id = models.CharField( _( "Id" ), max_length=16, primary_key=True )

    class Meta:
        abstract = True


def build_fake_pk( model, size=None ):
    if not size:
        max_length = model._meta.get_field( 'id' ).max_length
        size = max_length // 2
    return madness.string.generate_token_b64( length=size )


@receiver( pre_save )
def chibi_model_create_pk( sender, instance, **kw ):
    if not instance.pk and issubclass( sender, Chibi_model ):
        model_meta = sender._meta
        max_length = model_meta.get_field( 'id' ).max_length
        start = max_length // 2
        max_retry = 5
        count_retry = 0
        while True:
            try_pk = madness.string.generate_token_b64( length=start )
            is_pk_exists = sender.objects.filter( pk=try_pk ).exists()
            if not is_pk_exists:
                break
            logger.warning(
                "colicionarion coliciono el pk, incrementa "
                "la longitud de inicio",
                extra={
                    'number_pk_collide': 1, 'pk_collide': [ try_pk ],
                    'length_of_pk': start, 'count_of_retry': count_retry,
                    'max_length_pk': max_length,
                    'current_length': len( try_pk ),
                    'model': str( type( sender ) )
                } )
            if count_retry >= max_retry:
                start += 1
                count_retry += 1
                start = min( start, max_length )

        instance.pk = try_pk


class Header( models.Model ):
    key = models.CharField( max_length=128 )
    value_str = models.TextField( blank=True )

    class Meta:
        abstract = True

    def save( self, *args, **kw ):
        self.value = self.value
        super().save( *args, **kw )

    @property
    def value( self ):
        try:
            value = self._value
        except AttributeError:
            try:
                value = json.loads( self.value_str )
            except ( ValueError, TypeError ):
                value = self.value_str
        return value

    @value.setter
    def value( self, value ):
        if isinstance( value, str ):
            self.value_str = value
            self._value = value
        else:
            self.value_str = json.dumps( value )
            self._value = value

    def __str__( self ):
        return "{}: {}".format( self.key, self.value )

    def __repr__( self ):
        return "Header( key='{}' value={} )".format( self.key, self.value )

    def __eq__( self, other ):
        if not isinstance( other, Header ):
            return False
        return self.key == other.key and self.value == self.value


class ES_document( Document ):
    """
    clase basica para usar elastisearch con django
    """
    create_at = field.Date()
    update_at = field.Date()

    def save( self, *args, **kw ):
        if not getattr( self.meta, 'id', False ):
            if getattr( self, 'id', False ):
                self.meta.id = self.id
                del self.id
            if not getattr( self, 'create_at' ):
                self.create_at = datetime.datetime.utcnow()
        self.update_at = datetime.datetime.utcnow()
        return super().save( *args, **kw )
