###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.datetime import DateTime
from everysk.core.serialize import dumps, loads, CLASS_KEY
from everysk.core.unittests import TestCase, mock
from everysk.sdk.worker_base import WorkerBase
from everysk.sdk.engines.cache import UserCache
from everysk.sdk.engines.market_data import MarketData
from everysk.sdk.engines.expression import Expression
from everysk.sdk.engines.compliance import Compliance
from everysk.sdk.entities.portfolio.base import Portfolio
from everysk.sdk.entities.portfolio.security import Security
from everysk.sdk.entities.portfolio.securities import Securities
from everysk.sdk.entities.custom_index.base import CustomIndex
from everysk.sdk.entities.datastore.base import Datastore
from everysk.sdk.entities.file.base import File
from everysk.sdk.entities.private_security.base import PrivateSecurity
from everysk.sdk.entities.query import Query
from everysk.sdk.entities.report.base import Report
from everysk.sdk.entities.script import Script


@mock.patch.object(DateTime, 'now', mock.MagicMock(return_value=DateTime(2024, 6, 20, 14, 38, 59, 360554)))
class SerializeDumpsSDKTestCase(TestCase):
    maxDiff = None

    def test_sdk_objects_worker_base(self):
        self.assertEqual(
            dumps(WorkerBase({}), sort_keys=True),
            '{"%s": "everysk.sdk.worker_base.WorkerBase", "_errors": null, "_is_frozen": false, "_silent": false, "inputs_info": null, "parallel_info": null, "script_inputs": null, "worker_id": null, "worker_type": null, "workflow_execution_id": null, "workflow_id": null, "workspace": null}' % CLASS_KEY
        )

    def test_sdk_engines_objects_user_cache(self):
        self.assertEqual(
            dumps(UserCache(), sort_keys=True),
            '{"%s": "everysk.sdk.engines.cache.UserCache", "_errors": null, "_is_frozen": false, "_silent": false}' % CLASS_KEY
        )

    def test_sdk_engines_objects_market_data(self):
        self.assertEqual(
            dumps(MarketData(), sort_keys=True),
            '{"%s": "everysk.sdk.engines.market_data.MarketData", "_errors": null, "_is_frozen": false, "_silent": false, "date": null, "end_date": null, "nearest": false, "projection": null, "real_time": false, "start_date": null, "ticker_list": null, "ticker_type": null}' % CLASS_KEY
        )

    def test_sdk_engines_objects_expression(self):
        self.assertEqual(
            dumps(Expression(), sort_keys=True),
            '{"%s": "everysk.sdk.engines.expression.Expression", "_errors": null, "_is_frozen": false, "_silent": false}' % CLASS_KEY
        )

    def test_sdk_engines_objects_compliance(self):
        self.assertEqual(
            dumps(Compliance(), sort_keys=True),
            '{"%s": "everysk.sdk.engines.compliance.Compliance", "_errors": null, "_is_frozen": false, "_silent": false}' % CLASS_KEY
        )

    def test_sdk_entities_objects_portfolio(self):
        self.assertEqual(
            dumps(Portfolio(), sort_keys=True),
            '{"%s": "everysk.sdk.entities.portfolio.base.Portfolio", "base_currency": null, "check_securities": false, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "date": null, "description": null, "id": null, "level": null, "link_uid": null, "name": null, "nlv": null, "securities": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1", "workspace": null}' % CLASS_KEY
        )

    def test_sdk_entities_objects_security(self):
        self.assertEqual(
            dumps(Security(), sort_keys=True),
            '{"%s": "everysk.sdk.entities.portfolio.security.Security", "accounting": null, "asset_class": null, "asset_subclass": null, "book": null, "comparable": null, "cost_price": null, "coupon": null, '
            '"currency": null, "display": null, "error_message": null, "error_type": null, "exchange": null, "extra_data": null, "fx_rate": null, "hash": null, "id": null, "indexer": null, "instrument_class": null, "instrument_subtype": null, "instrument_type": null, "isin": null, "issue_date": null, '
            '"issue_price": null, "issuer": null, "issuer_type": null, "label": null, "look_through_reference": null, "market_price": null, "market_value": null, "market_value_in_base": null, "maturity_date": null, "multiplier": null, "name": null, "operation": null, "option_type": null, "percent_index": null, '
            '"premium": null, "previous_quantity": null, "quantity": null, "rate": null, "return_date": null, "series": null, "settlement": null, "status": null, "strike": null, "symbol": null, "ticker": null, "trade_id": null, "trader": null, "underlying": null, "unrealized_pl": null, "unrealized_pl_in_base": null, "warranty": null}' % CLASS_KEY
        )

    def test_sdk_entities_objects_securities(self):
        self.assertEqual(dumps(Securities(), sort_keys=True), '[]')

    def test_sdk_entities_objects_custom_index(self):
        self.assertEqual(
            dumps(CustomIndex(), sort_keys=True),
            '{"%s": "everysk.sdk.entities.custom_index.base.CustomIndex", "base_price": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "currency": null, "data": null, "data_type": null, "description": null, "id": null, "name": null, "periodicity": null, "symbol": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1"}' % CLASS_KEY
        )

    def test_sdk_entities_objects_datastore(self):
        self.assertEqual(
            dumps(Datastore(), sort_keys=True),
            '{"%s": "everysk.sdk.entities.datastore.base.Datastore", "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "data": null, "date": null, "description": null, "id": null, "level": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1", "workspace": null}' % CLASS_KEY
        )

    def test_sdk_entities_objects_file(self):
        self.assertEqual(
            dumps(File(), sort_keys=True),
            '{"%s": "everysk.sdk.entities.file.base.File", "content_type": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "data": null, "date": null, "description": null, "hash": null, "id": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "url": null, "version": "v1", "workspace": null}' % CLASS_KEY
        )

    def test_sdk_entities_objects_private(self):
        self.assertEqual(
            dumps(PrivateSecurity(), sort_keys=True),
            '{"%s": "everysk.sdk.entities.private_security.base.PrivateSecurity", "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "currency": null, "data": null, "description": null, "id": null, "instrument_type": null, "name": null, "symbol": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1"}' % CLASS_KEY
        )

    def test_sdk_entities_objects_query(self):
        self.assertEqual(
            dumps(Query(Portfolio), sort_keys=True),
            '{"%s": "everysk.sdk.entities.query.Query", "_clean_order": [], "_find_or_fail": false, "_klass": "Portfolio", "distinct_on": [], "filters": [], "limit": null, "offset": null, "order": [], "page_size": null, "page_token": null, "projection": null}' % CLASS_KEY
        )

    def test_sdk_entities_objects_report(self):
        self.assertEqual(
            dumps(Report(), sort_keys=True),
            '{"%s": "everysk.sdk.entities.report.base.Report", "authorization": null, "config_cascaded": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "date": null, "description": null, "id": null, "layout_content": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "url": null, "version": "v1", "widgets": null, "workspace": null}' % CLASS_KEY
        )

    def test_sdk_entities_objects_script(self):
        self.assertEqual(
            dumps(Script(Portfolio), sort_keys=True),
            '{"%s": "everysk.sdk.entities.script.Script", "_klass": "Portfolio"}' % CLASS_KEY
        )


@mock.patch.object(DateTime, 'now', mock.MagicMock(return_value=DateTime(2024, 6, 20, 14, 38, 59, 360554)))
class SerializeLoadsSDKTestCase(TestCase):

    def test_sdk_objects_worker_base(self):
        self.assertEqual(
            loads('{"%s": "everysk.sdk.app.worker_base.WorkerBase", "inputs_info": null, "parallel_info": null, "script_inputs": null, "worker_id": null, "worker_type": null, "workflow_execution_id": null, "workflow_id": null, "workspace": null}' % CLASS_KEY),
            WorkerBase({})
        )

    def test_sdk_engines_objects_user_cache(self):
        self.assertIsInstance(loads('{"%s": "everysk.sdk.app.engines.cache.UserCache"}' % CLASS_KEY), UserCache)

    def test_sdk_engines_objects_security(self):
        self.assertIsInstance(loads('{"%s": "everysk.sdk.app.engines.market_data.MarketData"}' % CLASS_KEY), MarketData)

    def test_sdk_engines_objects_market_data(self):
        self.assertIsInstance(loads('{"%s": "everysk.sdk.app.engines.expression.Expression"}' % CLASS_KEY), Expression)

    def test_sdk_engines_objects_compliance(self):
        self.assertIsInstance(loads('{"%s": "everysk.sdk.app.engines.compliance.Compliance"}' % CLASS_KEY), Compliance)

    def test_sdk_entities_objects_portfolio(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.portfolio.base.Portfolio", "base_currency": null, "check_securities": false, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "date": null, "description": null, "id": null, "level": null, "link_uid": null, "name": null, "nlv": null, "securities": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1", "workspace": null}' % CLASS_KEY),
            Portfolio()
        )

    def test_sdk_entities_objects_security(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.portfolio.security.Security", "accounting": null, "asset_class": null, "asset_subclass": null, "book": null, "comparable": null, "cost_price": null, "coupon": null, "currency": null, "display": null, "error_message": null, "error_type": null, "exchange": null, "extra_data": null, "fx_rate": null, "hash": null, "id": null, "indexer": null, "instrument_class": null, "instrument_subtype": null, "instrument_type": null, "isin": null, "issue_date": null, "issue_price": null, "issuer": null, "issuer_type": null, "label": null, "look_through_reference": null, "market_price": null, "market_value": null, "market_value_in_base": null, "maturity_date": null, "multiplier": null, "name": null, "operation": null, "option_type": null, "percent_index": null, "premium": null, "previous_quantity": null, "quantity": null, "rate": null, "return_date": null, "series": null, "settlement": null, "status": null, "strike": null, "symbol": null, "ticker": null, "trade_id": null, "trader": null, "underlying": null, "unrealized_pl": null, "unrealized_pl_in_base": null, "warranty": null}' % CLASS_KEY),
            Security()
        )

    def test_sdk_entities_objects_securities(self):
        self.assertEqual(loads('[]'), Securities())

    def test_sdk_entities_objects_custom_index(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.custom_index.base.CustomIndex", "base_price": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "currency": null, "data": null, "data_type": null, "description": null, "name": null, "periodicity": null, "symbol": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1"}' % CLASS_KEY),
            CustomIndex()
        )

    def test_sdk_entities_objects_datastore(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.datastore.base.Datastore", "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "data": null, "date": null, "description": null, "id": null, "level": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1", "workspace": null}' % CLASS_KEY),
            Datastore()
        )

    def test_sdk_entities_objects_file(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.file.base.File", "content_type": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "data": null, "date": null, "description": null, "hash": null, "id": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "url": null, "version": "v1", "workspace": null}' % CLASS_KEY),
            File()
        )

    def test_sdk_entities_objects_loads(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.private_security.base.PrivateSecurity", "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "currency": null, "data": null, "description": null, "instrument_type": null, "name": null, "symbol": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1"}' % CLASS_KEY),
            PrivateSecurity()
        )

    def test_sdk_entities_objects_query(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.query.Query", "_clean_order": [], "_klass": "Portfolio", "distinct_on": [], "filters": [], "limit": null, "offset": null, "order": [], "page_size": null, "page_token": null, "projection": null}' % CLASS_KEY),
            Query(Portfolio)
        )

    def test_sdk_entities_objects_report(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.report.base.Report", "authorization": null, "config_cascaded": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "date": null, "description": null, "id": null, "layout_content": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "url": null, "version": "v1", "widgets": null, "workspace": null}' % CLASS_KEY),
            Report()
        )

    def test_sdk_entities_objects_script(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.sdk.app.entities.script.Script", "_klass": "Portfolio"}' % CLASS_KEY),
            Script(Portfolio)
        )

    def test_sdk_entities_when_instantiate_object_is_false(self):
        p = Portfolio()
        result = dumps(p)
        res_loads = loads(result, instantiate_object=False)

        self.assertIsInstance(res_loads, dict)
        self.assertDictEqual(res_loads, Portfolio())
