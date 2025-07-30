"""
Settings for eox_core project meant to be called on the edx-platform/*/envs/aws.py module
"""
import logging

from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import

LOG = logging.getLogger(__name__)

try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
except ImportError:
    sentry_sdk = DjangoIntegration = None
    LOG.error("ImportError while importing %s", ImportError)


def plugin_settings(settings):  # pylint: disable=function-redefined
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/openedx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EOX_CORE_COMMENTS_SERVICE_USERS_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COMMENTS_SERVICE_USERS_BACKEND',
        settings.EOX_CORE_COMMENTS_SERVICE_USERS_BACKEND
    )
    settings.EOX_CORE_BEARER_AUTHENTICATION = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_BEARER_AUTHENTICATION',
        settings.EOX_CORE_BEARER_AUTHENTICATION
    )
    settings.EOX_CORE_USERS_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_USERS_BACKEND',
        settings.EOX_CORE_USERS_BACKEND
    )
    settings.EOX_CORE_ENROLLMENT_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_ENROLLMENT_BACKEND',
        settings.EOX_CORE_ENROLLMENT_BACKEND
    )
    settings.EOX_CORE_PRE_ENROLLMENT_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_PRE_ENROLLMENT_BACKEND',
        settings.EOX_CORE_PRE_ENROLLMENT_BACKEND
    )
    settings.EOX_CORE_CERTIFICATES_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_CERTIFICATES_BACKEND',
        settings.EOX_CORE_CERTIFICATES_BACKEND
    )
    settings.EOX_CORE_COURSEWARE_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COURSEWARE_BACKEND',
        settings.EOX_CORE_COURSEWARE_BACKEND
    )
    settings.EOX_CORE_GRADES_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_GRADES_BACKEND',
        settings.EOX_CORE_GRADES_BACKEND
    )
    settings.EOX_CORE_STORAGES_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_STORAGES_BACKEND',
        settings.EOX_CORE_STORAGES_BACKEND
    )

    settings.EOX_CORE_ENABLE_STATICFILES_STORAGE = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_ENABLE_STATICFILES_STORAGE',
        settings.EOX_CORE_ENABLE_STATICFILES_STORAGE
    )
    settings.EOX_CORE_STATICFILES_STORAGE = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_STATICFILES_STORAGE',
        settings.EOX_CORE_STATICFILES_STORAGE
    )
    if settings.EOX_CORE_ENABLE_STATICFILES_STORAGE:
        settings.STATICFILES_STORAGE = settings.EOX_CORE_STATICFILES_STORAGE

    settings.EOX_CORE_LOAD_PERMISSIONS = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_LOAD_PERMISSIONS',
        settings.EOX_CORE_LOAD_PERMISSIONS
    )
    settings.DATA_API_DEF_PAGE_SIZE = getattr(settings, 'ENV_TOKENS', {}).get(
        'DATA_API_DEF_PAGE_SIZE',
        settings.DATA_API_DEF_PAGE_SIZE
    )
    settings.DATA_API_MAX_PAGE_SIZE = getattr(settings, 'ENV_TOKENS', {}).get(
        'DATA_API_MAX_PAGE_SIZE',
        settings.DATA_API_MAX_PAGE_SIZE
    )
    settings.EOX_CORE_COURSES_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COURSES_BACKEND',
        settings.EOX_CORE_COURSES_BACKEND
    )
    settings.EOX_CORE_COURSEKEY_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COURSEKEY_BACKEND',
        settings.EOX_CORE_COURSEKEY_BACKEND
    )
    settings.EOX_CORE_COURSE_MANAGEMENT_REQUEST_TIMEOUT = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_COURSE_MANAGEMENT_REQUEST_TIMEOUT',
        settings.EOX_CORE_COURSE_MANAGEMENT_REQUEST_TIMEOUT
    )
    settings.EOX_CORE_THIRD_PARTY_AUTH_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_THIRD_PARTY_AUTH_BACKEND',
        settings.EOX_CORE_THIRD_PARTY_AUTH_BACKEND
    )
    settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_USER_ENABLE_MULTI_TENANCY',
        settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY
    )
    if not settings.EOX_CORE_USER_ENABLE_MULTI_TENANCY:
        user_origin_sources = [
            'fetch_from_unfiltered_table',
        ]
    else:
        user_origin_sources = settings.EOX_CORE_USER_ORIGIN_SITE_SOURCES
    settings.EOX_CORE_USER_ORIGIN_SITE_SOURCES = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_USER_ORIGIN_SITE_SOURCES',
        user_origin_sources
    )

    settings.EOX_CORE_APPEND_LMS_MIDDLEWARE_CLASSES = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_APPEND_LMS_MIDDLEWARE_CLASSES',
        settings.EOX_CORE_APPEND_LMS_MIDDLEWARE_CLASSES
    )
    if settings.SERVICE_VARIANT == "lms":
        if settings.EOX_CORE_APPEND_LMS_MIDDLEWARE_CLASSES:
            settings.MIDDLEWARE += [
                'eox_core.middleware.PathRedirectionMiddleware',
                'eox_core.middleware.RedirectionsMiddleware',
                'eox_core.middleware.TPAExceptionMiddleware'
            ]

    settings.MIDDLEWARE.insert(
        settings.MIDDLEWARE.index("openedx.core.djangoapps.lang_pref.middleware.LanguagePreferenceMiddleware") + 1,
        "eox_core.middleware.UserLanguagePreferenceMiddleware",
    )

    # Sentry Integration
    sentry_integration_dsn = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_SENTRY_INTEGRATION_DSN',
        settings.EOX_CORE_SENTRY_INTEGRATION_DSN
    )
    settings.EOX_CORE_SENTRY_IGNORED_ERRORS = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_SENTRY_IGNORED_ERRORS',
        settings.EOX_CORE_SENTRY_IGNORED_ERRORS
    )
    sentry_environment = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_SENTRY_ENVIRONMENT',
        settings.EOX_CORE_SENTRY_ENVIRONMENT
    )
    sentry_extra_options = getattr(settings, 'ENV_TOKENS', {}).get(
        'EOX_CORE_SENTRY_EXTRA_OPTIONS',
        settings.EOX_CORE_SENTRY_EXTRA_OPTIONS
    )

    if sentry_sdk is not None and sentry_integration_dsn is not None:
        from eox_core.integrations.sentry import ExceptionFilterSentry  # pylint: disable=import-outside-toplevel
        try:
            sentry_sdk.init(
                before_send=ExceptionFilterSentry(),
                dsn=sentry_integration_dsn,
                environment=sentry_environment,
                integrations=[
                    DjangoIntegration(),
                ],
                send_default_pii=True,
                **sentry_extra_options
            )
        except TypeError:
            sentry_sdk.init(
                before_send=ExceptionFilterSentry(),
                dsn=sentry_integration_dsn,
                environment=sentry_environment,
                integrations=[
                    DjangoIntegration(),
                ],
                send_default_pii=True
            )
