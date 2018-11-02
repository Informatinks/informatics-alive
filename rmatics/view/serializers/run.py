from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Integer(dumps_only=True)
    firstname = fields.String()
    lastname = fields.String()


class ProblemSchema(Schema):
    id = fields.Integer(dumps_only=True)
    name = fields.String()


class RunSchema(Schema):
    id = fields.Integer(dumps_only=True)
    user = fields.Nested(UserSchema)
    problem = fields.Nested(ProblemSchema)
    ejudge_status = fields.Integer()
    create_time = fields.DateTime()
