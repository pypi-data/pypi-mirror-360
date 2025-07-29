import unittest
from chibi_django.snippet.elasticsearch import build_index_name


class Test_build_index_name( unittest.TestCase ):
    def test_should_work( self ):
        result = build_index_name( "some_index" )
        self.assertEqual( 'test__some_index', result )
