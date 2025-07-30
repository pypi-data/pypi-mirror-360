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
from everysk.api.api_resources import Workflow, WorkflowExecution
from everysk.core.unittests import TestCase, mock


###############################################################################
#   Workflow TestCase Implementation
###############################################################################
class APIWorkflowTestCase(TestCase):

    def test_workflow_class_name_method(self):
        self.assertEqual(Workflow.class_name(), 'workflow')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_workflow_run_method(self, mock_create_api_requestor):
        mock_api_req = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_req
        mock_response_data = {'workflow_execution': {'id': 'workflow_id', 'other_details': 'data'}}
        mock_api_req.post.return_value = mock_response_data

        workflow_id = 'workflow_id'
        test_params = {'key1': 'value1', 'key2': 'value2'}
        result = Workflow.run(workflow_id, **test_params)
        expected_url = f'/workflows/{workflow_id}/run'

        mock_api_req.post.assert_called_with(expected_url, test_params)
        self.assertIsInstance(result, WorkflowExecution)
