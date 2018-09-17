from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.model import db
from rmatics.model.action import Action
from rmatics.testutils import TestCase


class TestModel__action_get_id(TestCase):
    def test_creates(self):
        description = 'description'
        action_id = Action.get_id(description)

        assert_that(action_id, equal_to(1))

        action = db.session.query(Action).filter_by(id=action_id).one()
        assert_that(
            action.description,
            equal_to('DESCRIPTION')
        )

    def test_reuses(self):
        description = 'description'
        action_id = Action.get_id(description)

        action_id2 = Action.get_id(description)
        assert_that(action_id, equal_to(action_id2))

        actions = db.session.query(Action).all()
        assert_that(len(actions), equal_to(1))
