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

from everysk.sdk.entities.worker_execution.base import WorkerExecution, ParallelInfo, Result, InputParams

###############################################################################
#   WorkerExecution TestCase Implementation
###############################################################################
class WorkerExecutionTestCase(TestCase):

    def setUp(self):
        self.worker_execution: WorkerExecution = WorkerExecution(
            id='wkex_df0fcbd647552fb6dcd6046be',
            result=Result(data={'output1': 'output1', 'output2': 'output2'}),
            storage=False,
            parallel_info=ParallelInfo(),
            status='FAILED',
            execution_type='MANUAL',
            start_time=DateTime(2023, 9, 9, 9, 9, 9, 9),
            end_time=DateTime(2023, 9, 9, 9, 9, 9, 9),
            workflow_execution_id='wfex_1234567891234567891234567',
            workflow_id='wrkf_1234567891234567891234567',
            workflow_name='My Workflow',
            worker_id='wrkr_1234567891234567891234567',
            worker_name='My Worker',
            worker_type='BASIC',
            created_on=DateTime(2023, 9, 9, 9, 9, 9, 9),
            updated_on=DateTime(2023, 9, 9, 9, 9, 9, 9),
            input_params=InputParams(
                worker_id='wrkr_1234567891234567891234567',
                workflow_id='wrkf_1234567891234567891234567',
                worker_execution_id='wkex_df0fcbd647552fb6dcd6046be',
                workflow_execution_id='wfex_1234567891234567891234567',
                workspace='main',
                worker_type='BASIC',
                script_inputs={'input1': 'input1', 'input2': 'input2'},
                inputs_info={'input1': 'input1', 'input2': 'input2'},
                parallel_info=ParallelInfo(),
            )
        )

        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_get_id_prefix(self):
        self.assertEqual(WorkerExecution.get_id_prefix(), settings.WORKER_EXECUTION_ID_PREFIX)

    def test_generate_id(self):
        self.assertRaisesRegex(
            NotImplementedError,
            '',
            WorkerExecution().generate_id
        )

    def test_query_load_with_id(self):
        expected_content = compress({'class_name': 'WorkerExecution', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'wkex_df0fcbd647552fb6dcd6046be', 'projection': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            WorkerExecution(id='wkex_df0fcbd647552fb6dcd6046be', workflow_execution_id='wfex_1234567891234567891234567').load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_query_load(self):
        worker_execution = WorkerExecution()
        expected_content = compress({'class_name': 'Query', 'method_name': 'load', 'self_obj': worker_execution.to_query().to_dict(add_class_path=True), 'params': {'offset': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            worker_execution.load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_to_dict(self):
        result = self.worker_execution.to_dict()
        expected_content = {
            'input_params': {
                'inputs_info': {'input1': 'input1', 'input2': 'input2'},
                'parallel_info': {'length': -1, 'index': -1},
                'script_inputs': {'input1': 'input1', 'input2': 'input2'},
                'worker_execution_id': 'wkex_df0fcbd647552fb6dcd6046be',
                'worker_id': 'wrkr_1234567891234567891234567',
                'worker_type': 'BASIC',
                'workflow_execution_id': 'wfex_1234567891234567891234567',
                'workflow_id': 'wrkf_1234567891234567891234567',
                'workspace': 'main',
            },
            'result': {
                'output1': 'output1',
                'output2': 'output2'
            },
            'cpu_time': 0.0,
            'created': 1694250549,
            'duration': 0.0,
            'id': 'wkex_df0fcbd647552fb6dcd6046be',
            'parallel_info': {'length': -1, 'index': -1},
            'process_cpu_time': 0.0,
            'started': 1694250549,
            'status': 'FAILED',
            'trigger': 'MANUAL',
            'updated': 1694250549,
            'version': 'v1',
            'worker_id': 'wrkr_1234567891234567891234567',
            'worker_name': 'My Worker',
            'worker_type': 'BASIC',
            'workflow_execution_id': 'wfex_1234567891234567891234567',
            'workflow_id': 'wrkf_1234567891234567891234567',
            'workflow_name': 'My Workflow',
        }

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_content)

        self.worker_execution.duration = None
        result = self.worker_execution.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_content)

    def test_get_input_params(self):
        self.assertRaisesRegex(
            ValueError,
            'Invalid Entity ID: invalid_id',
            WorkerExecution.get_input_params,
            'invalid_id'
        )

        with mock.patch('everysk.sdk.entities.worker_execution.base.WorkerExecution.retrieve', return_value=None) as mock_retrieve:
            self.assertRaisesRegex(
                ValueError,
                'Entity not found. Entity ID: wkex_df0fcbd647552fb6dcd6046be',
                WorkerExecution.get_input_params,
                'wkex_df0fcbd647552fb6dcd6046be'
            )

        mock_retrieve.assert_called_once_with('wkex_df0fcbd647552fb6dcd6046be')

        with mock.patch('everysk.sdk.entities.worker_execution.base.WorkerExecution.retrieve') as mock_retrieve:
            mock_retrieve.return_value = WorkerExecution(
                id='wkex_df0fcbd647552fb6dcd6046be',
                input_params=InputParams(),
                created_on=DateTime(2023, 9, 9, 9, 9, 9, 9),
                updated_on=DateTime(2023, 9, 9, 9, 9, 9, 9)
            )
            result = WorkerExecution.get_input_params('wkex_df0fcbd647552fb6dcd6046be')

        mock_retrieve.assert_called_once_with('wkex_df0fcbd647552fb6dcd6046be')
        self.assertEqual(
            result,
            InputParams(worker_execution_id='wkex_df0fcbd647552fb6dcd6046be')
        )

        with mock.patch('everysk.sdk.entities.worker_execution.base.WorkerExecution.retrieve') as mock_retrieve:
            mock_retrieve.return_value = WorkerExecution(
                id='wkex_df0fcbd647552fb6dcd6046be',
                input_params=InputParams(worker_execution_id='wkex_df0fcbd647552fb6dcd6046bc'),
                created_on=DateTime(2023, 9, 9, 9, 9, 9, 9),
                updated_on=DateTime(2023, 9, 9, 9, 9, 9, 9)
            )
            result = WorkerExecution.get_input_params('wkex_df0fcbd647552fb6dcd6046be')

        mock_retrieve.assert_called_once_with('wkex_df0fcbd647552fb6dcd6046be')
        self.assertEqual(
            result,
            InputParams(worker_execution_id='wkex_df0fcbd647552fb6dcd6046bc')
        )

    def test_to_query(self):
        result = WorkerExecution(workflow_execution_id='wfex_1234567891234567891234567').to_query()
        self.assertEqual(result, WorkerExecution.query.where('workflow_execution_id', 'wfex_1234567891234567891234567'))

    def test_init(self):
        self.assertEqual(
            WorkerExecution(
                result={'data': [1,2,3,4]},
                input_params={'workflow_execution_id': 'wfex_1234567891234567891234567'},
                parallel_info={'index': -1, 'length': -1},
                created_on=DateTime(2023, 9, 9, 9, 9, 9, 9),
                updated_on=DateTime(2023, 9, 9, 9, 9, 9, 9)
            ),
            WorkerExecution(
                result=Result(data= [1,2,3,4]),
                input_params=InputParams(workflow_execution_id='wfex_1234567891234567891234567'),
                parallel_info=ParallelInfo(index=-1, length=-1),
                created_on=DateTime(2023, 9, 9, 9, 9, 9, 9),
                updated_on=DateTime(2023, 9, 9, 9, 9, 9, 9)
            )
        )
