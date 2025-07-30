###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access
from google.api_core.exceptions import AlreadyExists, DeadlineExceeded, ServiceUnavailable, TooManyRequests
from everysk.core.compress import compress
from everysk.core.exceptions import FieldValueError, RequiredError
from everysk.core import workers
from everysk.core.workers import (
    BaseGoogle, CloudTasksClient, CreateTaskRequest, HttpMethod, log as worker_log,
    PauseQueueRequest, ResumeQueueRequest, TaskGoogle, WorkerGoogle
)
from everysk.core.unittests import TestCase, mock


class BaseGoogleTestCase(TestCase):

    def test_required_attributes(self):
        self.assertRaisesRegex(
            RequiredError,
            'The worker_id attribute is required.',
            BaseGoogle,
            google_task_project='bla',
            google_task_location='bla'
        )

    @mock.patch.object(workers, 'CloudTasksClient', spec=CloudTasksClient)
    def test_gtask(self, CloudTasksClient: mock.MagicMock): # pylint: disable=redefined-outer-name
        gtask = BaseGoogle(google_task_project='bla', google_task_location='bla', worker_id='bla')
        self.assertEqual(gtask._gtask, BaseGoogle._gtask)
        self.assertEqual(gtask.gtask, gtask._gtask)
        self.assertEqual(gtask.gtask, CloudTasksClient.return_value)


class FakeTask(TaskGoogle):
    google_task_location = 'location'
    google_task_project = 'project'
    worker_id = 'worker_id'
    worker_url = 'worker_url'

    def run(self) -> str:
        return super().run() or 'run'


@mock.patch.object(BaseGoogle, 'gtask', spec=CloudTasksClient)
class TaskGoogleTestCase(TestCase):

    def setUp(self) -> None:
        self.task = FakeTask()
        self.request = CreateTaskRequest(parent='queue_path', task={
            'name': 'task_path',
            'dispatch_deadline': {'seconds': 600},
            'http_request': {
                'http_method': HttpMethod.POST,
                'url': f'{self.task.worker_url}/worker/{self.task.worker_id}',
                'headers': self.task.get_headers(),
                'body': compress({
                    'cls': self.task.get_full_doted_class_path(),
                    'kwargs': self.task._received_kwargs
                }, serialize='pickle')
            }
        })

    def test_init(self, gtask: mock.MagicMock):
        task01 = FakeTask()
        task02 = FakeTask()
        task03 = FakeTask(google_task_name='test')
        self.assertNotEqual(task01.google_task_name, task02.google_task_name)
        self.assertNotEqual(task01.google_task_name, task03.google_task_name)
        self.assertNotEqual(task02.google_task_name, task03.google_task_name)
        self.assertEqual(task03.google_task_name, 'test')
        gtask.assert_not_called()

    def test_gtask_queue_path(self, gtask: mock.MagicMock):
        result = self.task.gtask_queue_path()
        gtask.queue_path.assert_called_once_with(project='project', location='location', queue='worker_id')
        self.assertEqual(result, gtask.queue_path.return_value)

    def test_gtask_task_path(self, gtask: mock.MagicMock):
        result = self.task.gtask_task_path()
        gtask.task_path.assert_called_once_with(
            project='project', location='location', queue='worker_id', task=self.task.google_task_name
        )
        self.assertEqual(result, gtask.task_path.return_value)

    def test_gtask_create_task_request(self, gtask: mock.MagicMock):
        gtask.task_path.return_value = 'task_path'
        gtask.queue_path.return_value = 'queue_path'
        result = self.task.gtask_create_task_request({
            'cls': self.task.get_full_doted_class_path(),
            'kwargs': self.task._received_kwargs
        })
        self.assertEqual(result, self.request)

    def test_get_headers(self, gtask: mock.MagicMock):
        self.assertEqual(self.task.get_headers(), {'Content-type': 'application/octet-stream'})
        gtask.assert_not_called()

    def test_run(self, gtask: mock.MagicMock):
        self.assertEqual(self.task.run(), 'run')
        gtask.assert_not_called()

    def test_send_start(self, gtask: mock.MagicMock):
        gtask.queue_path.return_value = 'queue_path'
        self.task.send_start()
        resume_queue_request = ResumeQueueRequest(name=self.task.gtask_queue_path())
        gtask.resume_queue.assert_called_once_with(request=resume_queue_request)

    def test_send_pause(self, gtask: mock.MagicMock):
        gtask.queue_path.return_value = 'queue_path'
        self.task.send_pause()
        pause_queue_request = PauseQueueRequest(name=self.task.gtask_queue_path())
        gtask.pause_queue.assert_called_once_with(request=pause_queue_request)

    def test_save(self, gtask: mock.MagicMock):
        gtask.task_path.return_value = 'task_path'
        gtask.queue_path.return_value = 'queue_path'
        self.task.save()
        gtask.create_task.assert_called_once_with(request=self.request, timeout=30)

    def test_save_timeout(self, gtask: mock.MagicMock):
        gtask.task_path.return_value = 'task_path'
        gtask.queue_path.return_value = 'queue_path'
        self.task.save(timeout=15)
        gtask.create_task.assert_called_once_with(request=self.request, timeout=15)

    def test_save_timeout_greater_30(self, gtask: mock.MagicMock):
        gtask.task_path.return_value = 'task_path'
        gtask.queue_path.return_value = 'queue_path'
        self.task.save(timeout=60)
        gtask.create_task.assert_called_once_with(request=self.request, timeout=30)

    @mock.patch.object(workers.log, 'debug')
    def test_save_retry_already_error(self, debug: mock.MagicMock, gtask: mock.MagicMock):
        gtask.task_path.return_value = 'task_path'
        gtask.queue_path.return_value = 'queue_path'
        gtask.create_task.side_effect = AlreadyExists('Error')
        call = mock.call(request=self.request, timeout=30)
        self.task.save(retry_times=1)
        gtask.create_task.assert_has_calls([call])
        debug.assert_called_once_with('Google task already exists: %s', 'task_path')

    def test_save_retry_deadline_error(self, gtask: mock.MagicMock):
        gtask.task_path.return_value = 'task_path'
        gtask.queue_path.return_value = 'queue_path'
        gtask.create_task.side_effect = DeadlineExceeded('Error')
        call = mock.call(request=self.request, timeout=30)
        with self.assertRaisesRegex(DeadlineExceeded, '504 Error'):
            self.task.save(retry_times=1)
        gtask.create_task.assert_has_calls([call, call])

    def test_save_retry_service_error(self, gtask: mock.MagicMock):
        gtask.task_path.return_value = 'task_path'
        gtask.queue_path.return_value = 'queue_path'
        gtask.create_task.side_effect = ServiceUnavailable('Error')
        call = mock.call(request=self.request, timeout=30)
        with self.assertRaisesRegex(ServiceUnavailable, '503 Error'):
            self.task.save(retry_times=1)
        gtask.create_task.assert_has_calls([call, call])

    def test_save_retry_429_error(self, gtask: mock.MagicMock):
        gtask.task_path.return_value = 'task_path'
        gtask.queue_path.return_value = 'queue_path'
        gtask.create_task.side_effect = TooManyRequests('Error')
        call = mock.call(request=self.request, timeout=30)
        with self.assertRaisesRegex(TooManyRequests, '429 Error'):
            self.task.save(retry_times=1)
        gtask.create_task.assert_has_calls([call, call])

    def test_deadline_min_value(self, gtask: mock.MagicMock):
        self.assertRaisesRegex(
            FieldValueError,
            "The value '14' for field 'timeout' must be between 15 and 1800.",
            FakeTask,
            timeout=14
        )
        gtask.assert_not_called()

    def test_deadline_max_value(self, gtask: mock.MagicMock):
        self.assertRaisesRegex(
            FieldValueError,
            "The value '1801' for field 'timeout' must be between 15 and 1800.",
            FakeTask,
            timeout=1801
        )
        gtask.assert_not_called()


class FakeWorker(WorkerGoogle):
    google_task_location = 'location'
    google_task_project = 'project'
    worker_id = 'worker_id'


class WorkerGoogleTestCase(TestCase):

    def test_check_google_task(self):
        worker = FakeWorker()
        headers = {'X-Cloudtasks-Queuename': 'worker_id', 'User-Agent': 'Google-Cloud-Tasks'}
        self.assertTrue(worker.check_google_task(headers))
        headers = {'X-Cloudtasks-Queuename': 'worker', 'User-Agent': 'Google-Cloud-Tasks'}
        self.assertFalse(worker.check_google_task(headers))
        headers = {'X-Cloudtasks-Queuename': 'worker_id', 'User-Agent': 'Google-Cloud'}
        self.assertFalse(worker.check_google_task(headers))

    @mock.patch.object(FakeTask, 'run', return_value='run_task')
    def test_run_task(self, run: mock.MagicMock):
        worker = FakeWorker()
        self.assertEqual(worker.run_task(FakeTask().get_full_doted_class_path(), {}), 'run_task')
        run.assert_called_once_with()

    @mock.patch.object(FakeTask, 'run', return_value='worker_run')
    def test_worker_run(self, run: mock.MagicMock):
        headers = {'X-Cloudtasks-Queuename': 'worker_id', 'User-Agent': 'Google-Cloud-Tasks'}
        data = compress({'cls': FakeTask().get_full_doted_class_path(), 'kwargs': {}}, serialize='pickle')
        self.assertDictEqual(
            FakeWorker.worker_run(headers, data),
            {'error': False, 'result': 'worker_run'}
        )
        run.assert_called_once_with()

    @mock.patch.object(FakeTask, 'run', side_effect=ValueError('Error'))
    @mock.patch.object(worker_log, 'error')
    @mock.patch.object(workers.traceback, 'format_exc', return_value='Traceback Error')
    def test_worker_run_error(self, format_exc: mock.MagicMock, log: mock.MagicMock, run: mock.MagicMock):
        headers = {'X-Cloudtasks-Queuename': 'worker_id', 'User-Agent': 'Google-Cloud-Tasks'}
        data = compress({'cls': FakeTask().get_full_doted_class_path(), 'kwargs': {}}, serialize='pickle')
        self.assertDictEqual(
            FakeWorker.worker_run(headers, data),
            {'error': True, 'message': 'Worker worker_id error: Error'}
        )
        run.assert_called_once_with()
        log.assert_called_once_with('Worker %s error: %s', 'worker_id', 'Traceback Error')
        format_exc.assert_called_once_with()

    @mock.patch.object(FakeTask, 'run', return_value='worker_run')
    @mock.patch.object(worker_log, 'error')
    def test_worker_run_check_fail(self, log: mock.MagicMock, run: mock.MagicMock):
        headers = {'X-Cloudtasks-Queuename': 'id', 'User-Agent': 'Google-Cloud-Tasks'}
        data = compress({'cls': FakeTask().get_full_doted_class_path(), 'kwargs': {}}, serialize='pickle')
        self.assertDictEqual(
            FakeWorker.worker_run(headers, data),
            {
                'error': True,
                'message': "Couldn't validate Google headers - {'X-Cloudtasks-Queuename': 'id', 'User-Agent': 'Google-Cloud-Tasks'}"
            }
        )
        run.assert_not_called()
        log.assert_called_once_with(
            "Couldn't validate Google headers - {'X-Cloudtasks-Queuename': 'id', 'User-Agent': 'Google-Cloud-Tasks'}"
        )

    @mock.patch.object(FakeTask, 'run', return_value='worker_run')
    @mock.patch.object(worker_log, 'error')
    def test_worker_run_worker_id(self, log: mock.MagicMock, run: mock.MagicMock):
        headers = {'X-Cloudtasks-Queuename': 'worker_id', 'User-Agent': 'Google-Cloud-Tasks'}
        data = compress({'cls': FakeTask().get_full_doted_class_path(), 'kwargs': {}}, serialize='pickle')
        self.assertDictEqual(
            FakeWorker.worker_run(headers, data, worker_id='new_id'),
            {
                'error': True,
                'message': "Couldn't validate Google headers - {'X-Cloudtasks-Queuename': 'worker_id', 'User-Agent': 'Google-Cloud-Tasks'}"
            }
        )
        run.assert_not_called()
        log.assert_called_once_with("Couldn't validate Google headers - {'X-Cloudtasks-Queuename': 'worker_id', 'User-Agent': 'Google-Cloud-Tasks'}")
