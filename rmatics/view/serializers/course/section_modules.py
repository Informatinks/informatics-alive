from marshmallow import fields, Schema

from rmatics.model.book import Book
from rmatics.model.label import Label
from rmatics.model.monitor import Monitor
from rmatics.model.resource import Resource
from rmatics.model.statement import Statement


class CourseStatementSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()


class CourseBookSchema(Schema):
    """ Serializer for Books links """
    pass


class CourseLabelSchema(Schema):
    """ Serializer for labels """
    pass


class CourseResourceSchema(Schema):
    """ Serializer for resources """
    pass


class CourseMonitorSchema(Schema):
    """ Serializer for monitors """
    pass


cls_schema_mapper = {
    Statement: CourseStatementSchema,
    Book: CourseBookSchema,
    Label: CourseLabelSchema,
    Resource: CourseLabelSchema,
    Monitor: CourseMonitorSchema,
}
