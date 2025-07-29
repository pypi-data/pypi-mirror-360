import unittest
from unittest.mock import patch
from chibi_django.models import ES_document


class Test_build_index_name( unittest.TestCase ):
    @patch( "elasticsearch_dsl.document.Document.save" )
    def test_should_work( self, save ):
        model = ES_document()
        self.assertFalse( model.create_at )
        self.assertFalse( model.update_at )
        model.save()
        save.assert_called_once()
        self.assertTrue( model.create_at )
        self.assertTrue( model.update_at )
