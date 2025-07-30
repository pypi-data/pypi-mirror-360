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
from everysk.core.exceptions import FieldValueError
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.base_list import EntityList


###############################################################################
#   Entity List TestCase Implementation
###############################################################################
class TestEntityList(TestCase):

    def setUp(self):
        self.entity_list = EntityList()

    def test_initialization_with_attributes(self):
        self.assertIsNone(self.entity_list.min_size)
        self.assertIsNone(self.entity_list.max_size)

    def test_ito_native(self):
        self.assertListEqual(self.entity_list.to_native(), [])

    def test_validate_called_on_init(self):
        # Mock _validate to check if it's called during initialization
        with mock.patch.object(EntityList, "_validate", return_value=None) as mock_validate:
            EntityList([1, 2, 3])
            self.assertEqual(mock_validate.call_count, 3)

    def test_validate_called_on_setitem(self):
        with mock.patch.object(EntityList, "_validate", return_value=None) as mock_validate:
            self.entity_list.append(1)
            self.entity_list[0] = 2
            self.assertEqual(mock_validate.call_count, 2)

    def test_validate_called_on_insert(self):
        with mock.patch.object(EntityList, "_validate", return_value=None) as mock_validate:
            self.entity_list.insert(0, 2)
            mock_validate.assert_called_once_with(2)

    def test_validate_called_on_append(self):
        with mock.patch.object(EntityList, "_validate", return_value=None) as mock_validate:
            self.entity_list.append(3)
            mock_validate.assert_called_once_with(3)

    def test_validate_called_on_extend(self):
        with mock.patch.object(EntityList, "_validate", return_value=None) as mock_validate:
            self.entity_list.extend([4, 5])
            # Should be called twice since there are two elements in the iterable
            self.assertEqual(mock_validate.call_count, 2)

    def test_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.entity_list.append(1)

    def test_derived_class_with_validation(self):
        class DerivedEntityList(EntityList):
            def _validate(self, value):
                if value < 0:
                    raise ValueError("Value should be non-negative!")
                return value

        derived_list = DerivedEntityList([1])
        self.assertListEqual(derived_list, [1])

        derived_list = DerivedEntityList()
        derived_list.append(1)
        self.assertRaisesRegex(
            ValueError,
            "Value should be non-negative!",
            derived_list.append,
            -1
        )

        self.assertRaisesRegex(
            FieldValueError,
            "Unsupported format.",
            DerivedEntityList,
            [['d']]
        )
