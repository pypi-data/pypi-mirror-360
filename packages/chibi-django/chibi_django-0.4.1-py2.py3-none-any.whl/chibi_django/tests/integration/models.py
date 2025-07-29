from django.db import connection
from django.db.models.base import ModelBase
from chibi_django.models import Chibi_model
from django.test import TestCase


class ModelMixinTestCase( TestCase ):
    @classmethod
    def setUpClass(cls):
        cls.model = ModelBase(
            '__TestModel__' + cls.model.__name__, ( cls.model, ),
            { '__module__': cls.model.__module__ }
        )

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(cls.model)
        super(ModelMixinTestCase, cls).setUpClass()


class Test_model( Chibi_model ):
    pass


class Test_chibi_model( ModelMixinTestCase ):
    model = Test_model

    def test_model_using_save( self ):
        model = Test_model()
        self.assertFalse( model.pk )
        model.save()
        model.refresh_from_db()
        self.assertTrue( model.pk )

    def test_model_using_save_twice_should_no_change_the_pk( self ):
        model = Test_model()
        self.assertFalse( model.pk )
        model.save()
        model.refresh_from_db()
        old_pk = model.pk
        model.save()
        self.assertEqual( old_pk, model.pk )

    def test_model_with_create( self ):
        model = Test_model.objects.create()
        self.assertTrue( model.pk )
        model.refresh_from_db()
        old_pk = model.pk
        model.save()
        self.assertEqual( old_pk, model.pk )
