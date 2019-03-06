from rmatics.model.cache_meta import MonitorCacheMeta
from rmatics.testutils import TestCase
from rmatics.utils.cacher import Cacher


class TestDBSearchString(TestCase):

    def test_get_invalidate_args(self):
        args = ['problem_1', 'problem_2']
        invalidate_args = MonitorCacheMeta.get_invalidate_args(args)
        self.assertEqual(invalidate_args, '|problem_1|problem_2|')

    def test_get_search_like_args(self):
        args = ['problem_1', 'problem_2']
        search_like = MonitorCacheMeta.get_search_like_args(args)
        self.assertEqual(search_like, ['%|problem_1|%', '%|problem_2|%'])


class TestCacheArgsToString(TestCase):
    def test_item_to_string(self):
        key = 'group_id'
        item = 4
        str_item = Cacher._simple_item_to_string(key, item)
        self.assertEqual(str_item, 'group_id_4')

    def test_list_item_to_key(self):
        key = 'group_id'
        value = [1, 2, 3]
        str_values = Cacher._list_item_to_string(key, value)
        self.assertEqual(str_values, ['group_id_1', 'group_id_2', 'group_id_3'])

    def test_kwargs_to_string_list(self):
        kwargs = {
            'group_id': 3,
            'problem_id': [1, 2, 3]
        }
        string_list = Cacher._kwargs_to_string_list(kwargs)
        expected_items = ['group_id_3', 'problem_id_1', 'problem_id_2', 'problem_id_3']

        for item in expected_items:
            self.assertIn(item, string_list)
