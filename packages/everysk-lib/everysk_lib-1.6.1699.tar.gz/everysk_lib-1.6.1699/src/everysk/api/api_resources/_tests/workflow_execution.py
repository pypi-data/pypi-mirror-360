###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.api.api_resources import WorkflowExecution
from everysk.core.unittests import TestCase, mock

###############################################################################
#   Workflow Execution TestCase Implementation
###############################################################################
class APIWorkflowExecutionTestCase(TestCase):

    def test_workflow_execution_class_name(self):
        self.assertEqual(WorkflowExecution.class_name(), 'workflow_execution')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_workflow_execution_retrieve_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_requestor

        workflow_id = '12345'
        mock_response_data = {'workflow_execution': {'key': 'data'}}
        mock_api_requestor.get.return_value = mock_response_data
        kwargs = {'param1': 'value1', 'param2': 'value2'}
        expected_url = f'/workflows/{workflow_id}/workflow_executions'
        result = WorkflowExecution.retrieve(workflow_id, **kwargs)

        mock_api_requestor.get.assert_called_once_with(expected_url, kwargs)
        self.assertIsInstance(result, WorkflowExecution)
        self.assertEqual(result['key'], 'data')

    @mock.patch('everysk.api.api_resources.worker_execution.WorkerExecution.retrieve')
    @mock.patch('everysk.api.api_resources.workflow_execution.WorkflowExecution.retrieve')
    @mock.patch('everysk.api.utils.sleep', return_value=None)
    def test_synchronous_retrieve_method(self, mock_sleep, mock_retrieve, mock_worker_retrieve):
        mock_retrieve.side_effect= [
            {'status': 'IN_PROGRESS', 'ender_worker_execution_id': 'worker1'},
            {'status': 'COMPLETED', 'ender_worker_execution_id': 'worker1'}
        ]
        worker_execution_result = {'worker_execution': 'result'}
        mock_worker_retrieve.return_value = worker_execution_result
        workflow_id = '12345'
        result = WorkflowExecution.syncronous_retrieve(workflow_id)

        self.assertEqual(mock_retrieve.call_count, 2)
        mock_retrieve.assert_any_call(workflow_id)
        mock_worker_retrieve.assert_called_once_with(worker_execution_id='worker1', with_result=True)
        self.assertEqual(result, worker_execution_result)
