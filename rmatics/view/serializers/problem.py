import json
from marshmallow import Schema, fields
from rmatics.model.problem import EjudgeProblem


class ProblemSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    content = fields.String()
    timelimit = fields.Float()
    memorylimit = fields.Integer()
    show_limits = fields.String()
    sample_tests_json = fields.Method(serialize='serialize_samples')
    output_only = fields.Boolean()

    def serialize_samples(self, obj: EjudgeProblem):
        obj.generateSamplesJson(force_update=True)
        return json.dumps(obj.sample_tests_json)
