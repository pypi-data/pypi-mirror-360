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
from everysk.core.datetime import DateTime
from everysk.core.exceptions import FieldValueError, RequiredError
from everysk.core.object import BaseDict
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.fields import EntityTagsField, CurrencyField, EntityNameField, EntityDescriptionField, EntityLinkUIDField, EntityWorkspaceField, EntityDateTimeField
from everysk.sdk.entities.tags import Tags


###############################################################################
#   Fields TestCase Implementation
###############################################################################
class _EntityNameTestAuxClass(BaseDict):
    required = EntityNameField()

class _EntityDescriptionFieldTestAuxClass(BaseDict):
    required = EntityDescriptionField()

class _EntityLinkUIDFieldTestAuxClass(BaseDict):
    required = EntityLinkUIDField()


class _EntityWorkspaceFieldTestAuxClass(BaseDict):
    required = EntityWorkspaceField()

class _EntityDateTimeFieldTestAuxClass(BaseDict):
    required = EntityDateTimeField()

class TestBaseCurrencyField(TestCase):

    def setUp(self):
        self.currency_field = CurrencyField(default="USD")

    def test_default_currencies(self):
        # Ensure the field was initialized with the correct set of default currencies
        self.assertIn(None, self.currency_field.choices)
        self.assertIn('USD', self.currency_field.choices)
        self.assertIn('BRL', self.currency_field.choices)

    def test_get_all_available_currencies(self):
        with mock.patch('everysk.sdk.engines.market_data.MarketData.get_currencies') as mock_get_currencies:
            mock_get_currencies.return_value = {'base_currencies': [
                ['USD', 'Us Dollar/Us Dollar Fx Spot Rate'],
                ['BRL', 'Brazilian Real/Brazilian Real Fx Spot Rate'],
                ['BTC', 'Bitcoin/Bitcoin Fx Spot Rate']
            ]}
            field = CurrencyField()

        self.assertEqual(field.choices, ['USD', 'BRL', 'BTC', None])
        self.assertEqual(field.default, None)
        self.assertEqual(field.required_lazy, True)
        self.assertEqual(field.required, False)
        mock_get_currencies.assert_called_once_with()


class TestEntityNameField(TestCase):

    def test_max_size(self):
        field = EntityNameField()
        self.assertRaisesRegex(
            FieldValueError,
            f"The length '{settings.ENTITY_NAME_MAX_LENGTH + 1}' for attribute 'banana' must be between '{settings.ENTITY_NAME_MIN_LENGTH}' and '{settings.ENTITY_NAME_MAX_LENGTH}'.",
            field.validate,
            attr_name='banana',
            value='a' * (settings.ENTITY_NAME_MAX_LENGTH + 1)
        )

    def test_min_size(self):
        field = EntityNameField()
        self.assertRaisesRegex(
            FieldValueError,
            f"The length '0' for attribute 'banana' must be between '{settings.ENTITY_NAME_MIN_LENGTH}' and '{settings.ENTITY_NAME_MAX_LENGTH}'.",
            field.validate,
            attr_name='banana',
            value=''
        )

    def test_required_lazy(self):
        cls = _EntityNameTestAuxClass()
        self.assertRaisesRegex(
            RequiredError,
            "The required attribute is required.",
            cls.validate_required_fields,
        )

    def test_empty_is_none(self):
        cls = _EntityNameTestAuxClass(required='')
        self.assertIsNone(cls.required)

class TestEntityDescriptionField(TestCase):

    def test_max_size(self):
        field = EntityDescriptionField()
        self.assertRaisesRegex(
            FieldValueError,
            f"The length '{settings.ENTITY_DESCRIPTION_MAX_LEN + 1}' for attribute 'banana' must be between '{settings.ENTITY_DESCRIPTION_MIN_LEN}' and '{settings.ENTITY_DESCRIPTION_MAX_LEN}'.",
            field.validate,
            attr_name='banana',
            value='a' * (settings.ENTITY_DESCRIPTION_MAX_LEN + 1)
        )

    def test_empty_is_none(self):
        cls = _EntityDescriptionFieldTestAuxClass(required='')
        self.assertIsNotNone(cls.required)

class TestEntityLinkUIDField(TestCase):

    def test_max_size(self):
        field = EntityLinkUIDField()
        self.assertRaisesRegex(
            FieldValueError,
            f"The length '{settings.ENTITY_LINK_UID_MAX_LENGTH + 1}' for attribute 'banana' must be between '{settings.ENTITY_LINK_UID_MIN_LENGTH}' and '{settings.ENTITY_LINK_UID_MAX_LENGTH}'.",
            field.validate,
            attr_name='banana',
            value='a' * (settings.ENTITY_LINK_UID_MAX_LENGTH + 1)
        )

    def test_min_size(self):
        field = EntityLinkUIDField()
        self.assertRaisesRegex(
            FieldValueError,
            f"The length '0' for attribute 'banana' must be between '{settings.ENTITY_LINK_UID_MIN_LENGTH}' and '{settings.ENTITY_LINK_UID_MAX_LENGTH}'.",
            field.validate,
            attr_name='banana',
            value=''
        )

    def test_empty_is_none(self):
        cls = _EntityLinkUIDFieldTestAuxClass(required='')
        self.assertIsNone(cls.required)

class TestEntityWorkspaceField(TestCase):

    def test_max_size(self):
        field = EntityWorkspaceField()
        self.assertRaisesRegex(
            FieldValueError,
            f"The length '{settings.ENTITY_WORKSPACE_MAX_LENGTH + 1}' for attribute 'banana' must be between '{settings.ENTITY_WORKSPACE_MIN_LENGTH}' and '{settings.ENTITY_WORKSPACE_MAX_LENGTH}'.",
            field.validate,
            attr_name='banana',
            value='a' * (settings.ENTITY_WORKSPACE_MAX_LENGTH + 1)
        )

    def test_min_size(self):
        field = EntityWorkspaceField()
        self.assertRaisesRegex(
            FieldValueError,
            f"The length '0' for attribute 'banana' must be between '{settings.ENTITY_WORKSPACE_MIN_LENGTH}' and '{settings.ENTITY_WORKSPACE_MAX_LENGTH}'.",
            field.validate,
            attr_name='banana',
            value=''
        )

    def test_required_lazy(self):
        cls = _EntityWorkspaceFieldTestAuxClass()
        self.assertRaisesRegex(
            RequiredError,
            "The required attribute is required.",
            cls.validate_required_fields,
        )

    def test_empty_is_none(self):
        cls = _EntityWorkspaceFieldTestAuxClass(required='')
        self.assertIsNone(cls.required)

class TestEntityDateTimeField(TestCase):

    def test_max_size(self):
        value = DateTime(2023, 12, 3, 12, 13, 14)
        with mock.patch('everysk.core.datetime.date_mixin.DateMixin.delta', return_value=DateTime(2023, 12, 2, 12, 13, 14)) as mock_delta:
            field = EntityDateTimeField()
            with self.assertRaises(FieldValueError) as e:
                field.validate(attr_name='banana', value=value)
            self.assertEqual(f"The value '{value}' for field 'banana' must be between {DateTime.market_start()} and {mock_delta.return_value.force_time('LAST_MINUTE')}.", e.exception.msg)

    def test_min_size(self):
        value = DateTime.market_start().delta(-1, 'D')
        with mock.patch('everysk.core.datetime.date_mixin.DateMixin.delta', return_value=DateTime(2023, 12, 2, 12, 13, 14)) as mock_delta:
            field = EntityDateTimeField()
            with self.assertRaises(FieldValueError) as e:
                field.validate(attr_name='banana', value=value)
            self.assertEqual(f"The value '{value}' for field 'banana' must be between {DateTime.market_start()} and {mock_delta.return_value.force_time('LAST_MINUTE')}.", e.exception.msg)

    def test_required_lazy(self):
        cls = _EntityDateTimeFieldTestAuxClass()
        self.assertRaisesRegex(
            RequiredError,
            "The required attribute is required.",
            cls.validate_required_fields,
        )

    def test_empty_is_none(self):
        cls = _EntityDateTimeFieldTestAuxClass(required='')
        self.assertIsNone(cls.required)

    @mock.patch.object(DateTime, 'now', return_value=DateTime(2023, 12, 28, 7, 13, 14))
    def test_validate(self, mock_now: mock.MagicMock):
        entity_cls = _EntityDateTimeFieldTestAuxClass(required='20231229')

        self.assertEqual(entity_cls.required, DateTime(2023, 12, 29, 12, 0, 0))
        with self.assertRaises(FieldValueError) as err:
            entity_cls.required = '20231230'
        self.assertEqual(
            f"The value '{DateTime(2023, 12, 30, 12, 0, 0)}' for field 'required' must be between {DateTime.market_start()} and {DateTime.now().delta(1, 'D').force_time('LAST_MINUTE')}.",
            err.exception.msg
        )
        with self.assertRaises(FieldValueError) as err:
            _EntityDateTimeFieldTestAuxClass(required='20231230')
        self.assertEqual(
            f"The value '{DateTime(2023, 12, 30, 12, 0, 0)}' for field 'required' must be between {DateTime.market_start()} and {DateTime.now().delta(1, 'D').force_time('LAST_MINUTE')}.",
            err.exception.msg
        )

        mock_now.return_value = DateTime(2023, 12, 29, 7, 13, 14)
        entity_cls = _EntityDateTimeFieldTestAuxClass(required='20231230')

        self.assertEqual(entity_cls.required, DateTime(2023, 12, 30, 12, 0, 0))
        with self.assertRaises(FieldValueError) as err:
            entity_cls.required = '20231231'
        self.assertEqual(
            f"The value '{DateTime(2023, 12, 31, 12, 0, 0)}' for field 'required' must be between {DateTime.market_start()} and {DateTime.now().delta(1, 'D').force_time('LAST_MINUTE')}.",
            err.exception.msg
        )
        with self.assertRaises(FieldValueError) as err:
            _EntityDateTimeFieldTestAuxClass(required='20231231')
        self.assertEqual(
            f"The value '{DateTime(2023, 12, 31, 12, 0, 0)}' for field 'required' must be between {DateTime.market_start()} and {DateTime.now().delta(1, 'D').force_time('LAST_MINUTE')}.",
            err.exception.msg
        )

class TestEntityTagsField(TestCase):

    def setUp(self):
        self.field = EntityTagsField()

    def test_clean_value_returns_tagslist_for_none(self):
        cleaned_value = self.field.clean_value(None)
        self.assertIsInstance(cleaned_value, Tags)
        self.assertEqual(len(cleaned_value), 0)

    def test_clean_value_converts_list_to_tagslist(self):
        initial_value = ['tag1', 'tag2']
        cleaned_value = self.field.clean_value(initial_value)
        self.assertIsInstance(cleaned_value, Tags)
        self.assertListEqual(cleaned_value, initial_value)

    def test_clean_value_accepts_tagslist(self):
        tags_list_value = Tags(['tag1', 'tag2'])
        cleaned_value = self.field.clean_value(tags_list_value)
        self.assertIs(cleaned_value, tags_list_value)

    def test_default_value_initialization(self):
        default_tags = ['default_tag']
        field_with_default = EntityTagsField(default=default_tags)
        self.assertIsInstance(field_with_default.default, Tags)
        self.assertListEqual(field_with_default.default, default_tags)
