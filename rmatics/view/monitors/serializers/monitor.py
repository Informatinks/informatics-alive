from marshmallow import fields, Schema

from rmatics.model import Problem
from rmatics.view.problem.serializers.run import UserRunSchema


class ProblemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    short_id = fields.Method(serialize='serialize_short_id')

    def serialize_short_id(self, obj: Problem):
        return obj.ejudge_problem.short_id


class RunSchema(Schema):
    id = fields.Integer(dump_only=True)
    user = fields.Nested(UserRunSchema, dump_only=True)
    create_time = fields.DateTime()
    ejudge_run_id = fields.Integer(dump_only=True, nullable=True)
    ejudge_contest_id = fields.Integer(dump_only=True,)
    ejudge_score = fields.Integer(dump_only=True)
    ejudge_status = fields.Integer(dump_only=True)
    ejudge_test_num = fields.Integer(dump_only=True)


class ContestMonitorSchema(Schema):
    contest_id = fields.Integer(dump_only=True)
    problem = fields.Nested(ProblemSchema, dump_only=True)
    runs = fields.List(fields.Dict(), dump_only=True)
