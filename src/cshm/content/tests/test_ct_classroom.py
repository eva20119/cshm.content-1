# -*- coding: utf-8 -*-
from cshm.content.content.classroom import IClassroom  # NOQA E501
from cshm.content.testing import CSHM_CONTENT_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName


class ClassroomIntegrationTest(unittest.TestCase):

    layer = CSHM_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_classroom_schema(self):
        fti = queryUtility(IDexterityFTI, name='Classroom')
        schema = fti.lookupSchema()
        self.assertEqual(IClassroom, schema)

    def test_ct_classroom_fti(self):
        fti = queryUtility(IDexterityFTI, name='Classroom')
        self.assertTrue(fti)

    def test_ct_classroom_factory(self):
        fti = queryUtility(IDexterityFTI, name='Classroom')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IClassroom.providedBy(obj),
            u'IClassroom not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_classroom_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Classroom',
            id='classroom',
        )
        self.assertTrue(
            IClassroom.providedBy(obj),
            u'IClassroom not provided by {0}!'.format(
                obj.id,
            ),
        )
