# This is an example test settings file for use with the Django test suite.
#
# The 'sqlite3' backend requires only the ENGINE setting (an in-
# memory database will be used). All other backends will require a
# NAME and potentially authentication information. See the
# following section in the docs for more information:
#
# http://docs.djangoproject.com/en/dev/internals/contributing/#unit-tests
#
# The different databases that Django supports behave differently in certain
# situations, so it is recommended to run the test suite against as many
# database backends as possible.  You may want to create a separate settings
# file for each of the backends you test against.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME'  : 'xe',
        'HOST'  : 'localhost',
        'USER'  : 'compositekey',
        'PASSWORD' : 'compositekey',
        'TEST_USER': 'django_test_default',
        'TEST_TBLSPACE': 'django_test_default',
        'TEST_TBLSPACE_TMP': 'django_test_default_temp',
    },
    'other': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME'  : 'xe',
        'HOST'  : 'localhost',
        'USER'  : 'compositekey',
        'PASSWORD' : 'compositekey',
        'TEST_USER': 'django_test_other',
        'TEST_TBLSPACE': 'django_test_other',
        'TEST_TBLSPACE_TMP': 'django_test_other_temp',
    }
}

SECRET_KEY = "django_tests_secret_key"
