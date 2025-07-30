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
from everysk.api.api_resources import WorkerExecution
from everysk.core.unittests import TestCase, mock


###############################################################################
#   Worker Execution TestCase Implementation
###############################################################################
class APIWorkerExecutionTestCase(TestCase):

    def test_worker_execution_class_name(self):
        self.assertEqual(WorkerExecution.class_name(), 'worker_execution')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_worker_execution_retrieve_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_requestor

        mock_response_data = {'worker_execution': {'key1': 'value1'}}
        mock_api_requestor.get.return_value = mock_response_data
        test_params = {'key1': 'value1'}
        response = WorkerExecution.retrieve(**test_params)
        expected_url = '/workflows/worker_executions'

        mock_api_requestor.get.assert_called_with(expected_url, test_params)
        self.assertIsInstance(response, WorkerExecution)
