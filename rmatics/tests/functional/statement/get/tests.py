from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
)

from rmatics.testutils import TestCase


class TestAPI__statement_get(TestCase):
    def setUp(self):
        super(TestAPI__statement_get, self).setUp()

        self.create_statements()

    def test_simple(self):
        response = self.client.get(f'/statement/{self.statements[0].id}')
        assert_that(
            response.json,
            has_entries({
                'id': self.statements[0].id,
            })
        )
    
    def test_not_found(self):
        response = self.client.get('/statement/179')
        assert_that(response.status_code, equal_to(404))
        assert_that(
            response.json,
            equal_to({
                'code': 404,
                'message': 'No statement with this id'
            })
        )
