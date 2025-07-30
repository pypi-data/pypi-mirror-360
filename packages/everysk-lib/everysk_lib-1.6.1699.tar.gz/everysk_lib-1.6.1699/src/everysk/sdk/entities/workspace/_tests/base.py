###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.config import settings
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock
from everysk.core.compress import compress

from everysk.sdk.entities.workspace.base import Workspace
###############################################################################
#   Workspace TestCase Implementation
###############################################################################
class TestWorkspace(TestCase):

    def setUp(self):
        self.sample_data = {
            'name': 'main',
            'description': 'Description',
            'group': 'Test'
        }
        self.workspace = Workspace(**self.sample_data)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_static_methods(self):
        self.assertEqual(Workspace.get_id_prefix(), settings.WORKSPACE_ID_PREFIX)

    def test_query_load_with_id(self):
        workspace = Workspace(id='main', group='Test')
        expected_content = compress({'class_name': 'Workspace', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'main', 'projection': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            workspace.load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_generate_id(self):
        self.assertRaisesRegex(
            NotImplementedError,
            '',
            Workspace().generate_id
        )

    def test_to_dict(self):
        dct = self.workspace.to_dict()
        self.assertEqual(dct['description'], 'Description')
        self.assertEqual(dct['group'], 'Test')
        self.assertEqual(dct['name'], 'main')

        self.workspace.description = None
        dct = self.workspace.to_dict()
        self.assertEqual(dct['description'], '')
        self.assertEqual(dct['group'], 'Test')
        self.assertEqual(dct['name'], 'main')

    def test_workspace_id(self):
        self.assertEqual(self.workspace.id, 'main')
        self.workspace.id = 'main2'
        self.assertEqual(self.workspace.name, 'main2')
        self.assertEqual(self.workspace.id, 'main2')
        self.workspace.name = 'main3'
        self.assertEqual(self.workspace.id, 'main3')
        self.assertEqual(self.workspace.name, 'main3')
        self.workspace.id = None
        self.assertEqual(self.workspace.id, None)
        self.assertEqual(self.workspace.name, None)
