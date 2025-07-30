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
from everysk.core.datetime import DateTime, Date
from everysk.core.exceptions import FieldValueError
from everysk.core.unittests import TestCase

from everysk.sdk.entities.tags import Tags


###############################################################################
#   Tags TestCase Implementation
###############################################################################
class TagsTestCase(TestCase):

    def test_append_valid_tag(self):
        valid_tag = 'valid_tag'

        tags = Tags()
        tags.append(valid_tag)
        self.assertIn(valid_tag, tags)

    def test_append_invalid_tag(self):
        invalid_tag = {'a': 'b'}

        tags = Tags()
        with self.assertRaises(FieldValueError, msg="Tags: The string value does not match the required pattern"):
            tags.append(invalid_tag)

    def test_append_none_tag(self):
        tags = Tags()
        tags.append(None)
        self.assertListEqual(['none'], tags)

    def test_append_empty_tag(self):
        empty_tag = ''
        tags = Tags()
        tags.append(empty_tag)
        self.assertIn('none', tags)

    def test_append_float_tag(self):
        float_tag = 1.0
        tags = Tags()
        tags.append(float_tag)
        self.assertIn('1_0', tags)

    def test_append_long_tag(self):
        long_tag = 'a' * (settings.ENTITY_MAX_TAG_LENGTH + 1)
        tags = Tags()
        with self.assertRaises(FieldValueError, msg=f"Tags: '{long_tag}' size it's not between {tags.min_size} and {settings.ENTITY_MAX_TAG_LENGTH}"):
            tags.append(long_tag)

    def test_tag_sanitizes(self):
        tags = Tags(123)
        self.assertListEqual(['123'], tags)

        tags = Tags(123.321)
        self.assertListEqual(['123_321'], tags)

        tags = Tags(['tag'])
        self.assertListEqual(['tag'], tags)

        tags = Tags(['tag#123'])
        self.assertListEqual(['tag_123'], tags)

        tags = Tags(['Tag#123'])
        self.assertListEqual(['tag_123'], tags)

        tags = Tags(['T123!TT23'])
        self.assertListEqual(['t123_tt23'], tags)

        tags = Tags([123.321])
        self.assertListEqual(['123_321'], tags)

        #add a duplicate tag
        tags = Tags(['tag1', 'tag2', 'tag1'])
        self.assertListEqual(['tag1', 'tag2'], tags)

        tags = Tags('tag1')
        self.assertListEqual(['t', 'a', 'g', '1'], tags)

        tags = Tags(['tag1', 'tag2'])
        self.assertListEqual(['tag1', 'tag2'], tags)

        tags = Tags([['tag1', 'tag2'], ['tag1', 'tag3']])
        self.assertListEqual(['tag1', 'tag2', 'tag3'], tags)

        tags = Tags([['tag1', 'tag2'], ['tag1', 'tag3'], []])
        self.assertListEqual(['tag1', 'tag2', 'tag3'], tags)

        tags = Tags([[None, 'tag2'], ['tag1', Undefined, 'tag3'], ['', 'tag4']])
        self.assertListEqual(['none', 'tag2', 'tag1', 'tag3', 'tag4'], tags)

        # empty tag
        tags = Tags()
        self.assertListEqual([], tags)

        self.assertRaisesRegex(
            FieldValueError,
            "Unsupported format in Tags.",
            Tags,
            ['tag1', 'tag2', {'a': 'b'}]
        )

        self.assertRaisesRegex(
            FieldValueError,
            "Unsupported format in Tags.",
            Tags,
            [['tag1', 'tag2'], ['tag1', 'tag2', {'a': 'b'}]]
        )

    def test_extend_tags(self):
        tags = Tags(['tag1', 'tag2'])
        tags.extend(['tag3', 'tag4'])
        self.assertListEqual(['tag1', 'tag2', 'tag3', 'tag4'], tags)

        tags = Tags(['Tag#123', 'tag2'])
        tags.extend(['tag3', 'Tag!321'])
        self.assertListEqual(['tag_123', 'tag2', 'tag3', 'tag_321'], tags)

        #add a duplicate tag
        tags = Tags(['tag1', 'tag2'])
        tags.extend(['tag3', 'tag2'])
        self.assertListEqual(['tag1', 'tag2', 'tag3'], tags)

        tags = Tags(['tag1', 'tag2'])
        self.assertRaisesRegex(
            FieldValueError,
            "Unsupported format in Tags: <class 'dict'>",
            tags.extend,
            [{'a': 'b'}]
        )

    def test_insert(self):
        tags = Tags(['tag1', 'tag2'])
        tags.insert(0, 'tag3')
        self.assertListEqual(['tag3', 'tag1', 'tag2'], tags)

        tags = Tags(['tag1', 'tag2'])
        tags.insert(1, 'tag3')
        self.assertListEqual(['tag1', 'tag3', 'tag2'], tags)

        tags = Tags(['tag1', 'tag2'])
        self.assertRaisesRegex(
            FieldValueError,
            "Unsupported format in Tags: <class 'list'>",
            tags.insert,
            2,
            ['tag3', 'tag4']
        )

    def test__setitem__(self):
        tags = Tags(['tag1', 'tag2'])
        tags[0] = 'tag3'
        self.assertListEqual(['tag3', 'tag2'], tags)

        tags = Tags(['tag1', 'tag2'])
        tags[1] = 'tag3'
        self.assertListEqual(['tag1', 'tag3'], tags)

        tags = Tags(['tag1', 'tag2'])
        self.assertRaisesRegex(
            FieldValueError,
            "Unsupported format in Tags: <class 'list'>",
            tags.__setitem__,
            2,
            ['tag3', 'tag4']
        )

        class Fake:
            pass

        tags = Tags(['tag1', 'tag2'])
        self.assertRaisesRegex(
            FieldValueError,
            "Unsupported format in Tags: <class 'everysk.sdk.entities._tests.tags.TagsTestCase.test__setitem__.<locals>.Fake'>",
            tags.__setitem__,
            2,
            Fake()
        )

    def test_unify_tags(self):
        tags = Tags.unify([['tag1', 'tag2'], ['tag3', 'tag4']], ['tag5', 'tag6'])
        self.assertListEqual(['tag1', 'tag2', 'tag3', 'tag4'], tags)

        tags = Tags.unify([['tag1', 'tag2'], ['tag3', 'tag4']], [])
        self.assertListEqual(['tag1', 'tag2', 'tag3', 'tag4'], tags)

        tags = Tags.unify([['tag1', 'tag2'], ['tag3', 'tag4']], None)
        self.assertListEqual(['tag1', 'tag2', 'tag3', 'tag4'], tags)

        tags = Tags.unify([None, ['tag3', 'tag4']], ['tag1', 'tag2'])
        self.assertListEqual(['tag1', 'tag2', 'tag3', 'tag4'], tags)

        tags = Tags.unify([['tag1', 'tag2'], ['tag3', 'tag4']], ['tag1', 'tag2', 'tag3', 'tag4'])
        self.assertListEqual(['tag1', 'tag2', 'tag3', 'tag4'], tags)

        tags = Tags.unify([None], ['tag1', 'tag2'])
        self.assertListEqual(['tag1', 'tag2'], tags)

        tags = Tags.unify(None, ['tag1', 'tag2'])
        self.assertListEqual([], tags)

        tags = Tags.unify([], ['tag1', 'tag2'])
        self.assertListEqual([], tags)

        tags = Tags.unify(['tag1'], ['tag1', 'tag2'])
        self.assertListEqual(['tag1'], tags)

        tags = Tags.unify([['tag1']], ['tag1', 'tag2'])
        self.assertListEqual(['tag1'], tags)

        tags = Tags.unify([None], ['tag1', 'tag2'])
        self.assertListEqual(['tag1', 'tag2'], tags)

        tags = Tags.unify([[]], ['tag1', 'tag2'])
        self.assertListEqual(['tag1', 'tag2'], tags)

        tags = Tags.unify([DateTime(2023, 9, 9, 9, 9, 9, 999)], [None, 'tag1', 'tag2'])
        self.assertListEqual(['20230909'], tags)

        tags = Tags.unify([Date(2023, 9, 9)], [None, 'tag1', 'tag2'])
        self.assertListEqual(['20230909'], tags)

        tags = Tags.unify([True, False], [None, 'tag1', 'tag2'])
        self.assertListEqual(['true', 'false'], tags)

        tags = Tags.unify([[None]], [None, 'tag1', 'tag2'])
        self.assertListEqual(['none', 'tag1', 'tag2'], tags)

        tags = Tags.unify([[None]], ['tag1', 'tag2'])
        self.assertListEqual(['tag1', 'tag2'], tags)

        tags = Tags.unify(['tag3', ['tag3'], None, [], [None]], ['tag1', 'tag2'])
        self.assertListEqual(['tag3', 'tag1', 'tag2'], tags)

        tags = Tags.unify(['', [''], None], ['tag1', 'tag2'])
        self.assertListEqual(['tag1', 'tag2'], tags)
