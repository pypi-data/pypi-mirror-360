import os
from unittest.suite import TestSuite

from django.conf import settings
from django.test.runner import DiscoverRunner


# sys.stdout = None
# requests.packages.urllib3.disable_warnings( InsecureRequestWarning )


class CustomizedRunner( DiscoverRunner ):
    def __init__( self, *args, **kw ):
        super().__init__( *args, **kw )

    def build_suite(self, *args, **kwargs):
        suite = super().build_suite( *args, **kwargs )
        filtered = TestSuite()

        for test in suite:
            testname = str( test )
            if 'unittest.loader._FailedTest' in testname.lower():
                print( testname )
            if '.tests.' in testname and self.package in testname:
                filtered.addTest( test )
        return filtered

    def setup_test_environment( self, **kargs ):
        settings.TEST_MODE = True
        super().setup_test_environment( **kargs )
        settings.CELERY_ALWAYS_EAGER = True
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75
        settings.DEBUG = False


class UnitRunner( CustomizedRunner ):
    package = '.unit.'

    def setup_databases( self, *args, **kwargs ):
        pass

    def teardown_databases( self, *args, **kwargs ):
        pass


class IntegrationRunner( CustomizedRunner ):
    package = '.integration.'


class AcceptanceRunner( CustomizedRunner ):
    package = '.acceptance.'
    os.environ[ 'DJANGO_LIVE_TEST_SERVER_ADDRESS' ] = 'localhost:8001'
