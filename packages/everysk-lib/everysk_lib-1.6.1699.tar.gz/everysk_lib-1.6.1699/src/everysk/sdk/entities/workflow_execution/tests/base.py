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
from everysk.core.compress import compress
from everysk.core.datetime import DateTime
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.workflow_execution.base import WorkflowExecution

###############################################################################
#   WorkflowExecution TestCase Implementation
###############################################################################
class WorkflowExecutionTestCase(TestCase):

    def setUp(self):
        self.workflow_execution: WorkflowExecution = WorkflowExecution(
            id='wfex_1234567891234567891234567',
            status='COMPLETED',
            run_status='FAILED',
            execution_type='MANUAL',
            start_time=DateTime(2023, 9, 9, 9, 9, 9, 9),
            end_time=DateTime(2023, 9, 9, 9, 9, 9, 9),
            workflow_id='wrkf_1234567891234567891234567',
            workflow_name='My Workflow',
            workspace='main',

            started_worker_id='wrkr_1234567891234567891234567',
            ender_worker_id='wrkr_1234567891234567891234568',
            ender_worker_execution_id='wkex_df0fcbd647552fb6dcd6046be',
            _managed_user=False,
            created_on=DateTime(2023, 9, 9, 9, 9, 9, 9),
            updated_on=DateTime(2023, 9, 9, 9, 9, 9, 9),
        )

        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_get_id_prefix(self):
        self.assertEqual(WorkflowExecution.get_id_prefix(), settings.WORKFLOW_EXECUTION_ID_PREFIX)

    def test_query_load_with_id(self):
        expected_content = compress({'class_name': 'WorkflowExecution', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'wfex_1234567891234567891234567', 'projection': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            WorkflowExecution(id='wfex_1234567891234567891234567').load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_query_load(self):
        workflow_execution = WorkflowExecution()
        expected_content = compress({'class_name': 'Query', 'method_name': 'load', 'self_obj': workflow_execution.to_query().to_dict(add_class_path=True), 'params': {'offset': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            workflow_execution.load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_to_dict(self):
        result = self.workflow_execution.to_dict()
        expected_data = {
            'status': 'COMPLETED',
            'run_status': 'FAILED',
            'real_execution_time': None,
            'started_worker_id': 'wrkr_1234567891234567891234567',
            'workflow_id': 'wrkf_1234567891234567891234567',
            'version': 'v1',
            '_managed_user': False,
            'ender_worker_execution_id': 'wkex_df0fcbd647552fb6dcd6046be',
            'workflow_name': 'My Workflow',
            'workspace': 'main',
            'duration': None,
            'id': 'wfex_1234567891234567891234567',
            'ender_worker_id': 'wrkr_1234567891234567891234568',
            'total_execution_time': None,
            'created': 1694250549,
            'updated': 1694250549,
            'started': 1694250549,
            'trigger': 'MANUAL',
            'resume': None
        }

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_data)

    def test_to_query(self):
        result = WorkflowExecution(workflow_id='wrkf_1234567891234567891234567').to_query()
        self.assertEqual(result, WorkflowExecution.query.where('workflow_id', 'wrkf_1234567891234567891234567'))
