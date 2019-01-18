from marshmallow import Schema, fields


class UserRunSchema(Schema):
    id = fields.Integer(dumps_only=True)
    firstname = fields.String()
    lastname = fields.String()


class ProblemRunSchema(Schema):
    id = fields.Integer(dumps_only=True)
    name = fields.String()


class RunSchema(Schema):
    id = fields.Integer(dumps_only=True)
    user = fields.Nested(UserRunSchema)
    problem = fields.Nested(ProblemRunSchema)
    ejudge_status = fields.Integer()
    create_time = fields.DateTime()
    ejudge_language_id = fields.Integer()
    ejudge_test_num = fields.Integer()
    ejudge_score = fields.Integer()
