try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

# here = os.path.abspath( os.path.dirname( __file__ ) )
# README = open(os.path.join( here, 'README.rst' ) ).read()

setup(
    name='chibi_django',
    version='0.4.1',
    description='',
    # long_description=README,
    license='',
    author='',
    author_email='',
    packages=find_packages(include=[
        'chibi_django', 'chibi_django.*',
        'chibi_user', 'chibi_user.*',
        'test_runners', 'test_runners.*' ] ),
    install_requires=[
        'Django>=2.0.7', 'django-filter>=2.0.7',
        'djangorestframework>=3.8.2',
        'drf-nested-routers>=0.90.2',
        'chibi>=0.7.7', 'chibi_donkey>=1.0.0', 'chibi_auth0>=0.1.0'
    ],
    dependency_links = [],
    url='https://github.com/dem4ply/chibi_django',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
