# -*- coding: utf-8 -*-
""" Tests for public user creation API. """
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

import eox_core
from eox_core.api.v1.views import UserInfo
from eox_core.test_utils import SuperUserFactory

JSON_CONTENT_TYPE = 'application/json'


class TestInfoView(TestCase):
    """ Tests for the eox-info page """

    def test_version_is_present(self):
        """ Check that test version is present """
        response = self.client.get('/eox-info')
        self.assertContains(response, eox_core.__version__)

    def test_userinfo_endpoint(self):
        """ Tests for /userinfo/ """
        factory = APIRequestFactory()
        view = UserInfo.as_view()
        request = factory.get('/api/v1/userinfo', content_type='application/json')
        user = SuperUserFactory()
        force_authenticate(request, user=user)
        response = view(request)
        response_json = response.data
        self.assertIn('user', response_json)
        self.assertDictEqual(
            response_json, {
                'is_superuser': True,
                'is_staff': True,
                'user': 'robot0',
                'auth': 'None',
                'email': 'robot+test+0@example.com'
            }
        )
