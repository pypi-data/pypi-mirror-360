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
from everysk.core.object import BaseDict
from everysk.core.unittests import TestCase, mock

from everysk.sdk.worker_base import WorkerBase


###############################################################################
#   Worker Base Test Case Implementation
###############################################################################
class WorkerBaseTestCase(TestCase):
    def setUp(self) -> None:
        self.args = BaseDict(
            workspace='update_test',
            script_inputs=BaseDict(key='value'),
            inputs_info=BaseDict(key='987'),
            worker_type='type7',
            parallel_info=BaseDict(key='567'),
            worker_id='wrk_4567',
            workflow_id='wrk_flow_23132',
            workflow_execution_id='wrk_flow_exec_123'
        )
        self.kwargs = {
            'workspace': 'test',
            'val_1': 1,
            'val_2': {'key': 'val'},
            'val_3': [Undefined, None, 1, 'text']
        }
        self.worker_base = WorkerBase(self.args, **self.kwargs)
        return super().setUp()

    def test_worker_base_init(self):
        expected_dict = WorkerBase()
        expected_dict.workspace = 'update_test'
        expected_dict.script_inputs = BaseDict(key='value')
        expected_dict.inputs_info = BaseDict(key='987')
        expected_dict.worker_type = 'type7'
        expected_dict.parallel_info = BaseDict(key='567')
        expected_dict.worker_id = 'wrk_4567'
        expected_dict.workflow_id = 'wrk_flow_23132'
        expected_dict.workflow_execution_id = 'wrk_flow_exec_123'
        expected_dict.val_1 = 1
        expected_dict.val_2 = {'key': 'val'}
        expected_dict.val_3 = [Undefined, None, 1, 'text']

        self.assertEqual(WorkerBase(self.args, **self.kwargs), expected_dict)

    def test_handle_inputs_worker_base(self):
        self.worker_base.handle_inputs()
        self.assertEqual(self.worker_base.key, 'value')

    def test_handle_outputs_worker_base(self):
        with self.assertRaises(NotImplementedError):
            self.worker_base.handle_outputs()

    def test_handle_tasks_worker_base(self):
        with self.assertRaises(NotImplementedError):
            self.worker_base.handle_tasks()

    def test_run_worker_base(self):
        with self.assertRaises(NotImplementedError):
            with mock.patch('everysk.sdk.worker_base.WorkerBase.handle_inputs'):
                with mock.patch('everysk.sdk.worker_base.WorkerBase.handle_tasks'):
                    self.worker_base.run()
