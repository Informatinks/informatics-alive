from marshmallow import fields, Schema

from rmatics.model.course import Course
from rmatics.model.course_module import CourseModule
from rmatics.model.course_section import CourseSection
from rmatics.view.course.serializers.section_modules import cls_schema_mapper


class CourseSchema(Schema):
    id = fields.Integer()
    full_name = fields.String()
    short_name = fields.String()
    sections = fields.Method(serialize='serialize_sections')
    require_password = fields.Method(serialize='serialize_require_password')

    def serialize_sections(self, obj: Course):
        if obj.require_password():
            return None
        sections = obj.sections
        schema = CourseSectionSchema(many=True)
        return schema.dump(sections).data

    def serialize_require_password(self, obj) -> bool:
        return obj.require_password()


class CourseSectionSchema(Schema):
    id = fields.Integer()
    course_id = fields.Integer()
    section = fields.Integer()
    summary = fields.String()
    sequence = fields.String()
    visible = fields.Boolean()
    modules = fields.Method(serialize='serialize_modules')

    def serialize_modules(self, obj: CourseSection):
        # TODO: перенести запрос в БД во views
        module = obj.modules.filter_by(visible=True).all()
        schema = CourseSectionModuleSchema(many=True)
        return schema.dump(module).data


# Что это такое: CourseModule самописная реализация ContentType
# module -- некая "метка", какая таблица (и какой класс)
# на самом деле отвечают за этот CourseModule
# Возможные варианты: (Statement, Book, Label, Resource, Monitor, )
# Но Book, Label, Resource и Monitor пока не нужны
class CourseSectionModuleSchema(Schema):
    id = fields.Integer()
    course_id = fields.Integer()
    module = fields.Integer()
    section_id = fields.Integer()
    visible = fields.Boolean()
    type = fields.Method(serialize='serialize_type')
    instance = fields.Method(serialize='serialize_instance')

    def serialize_type(self, obj: CourseModule):
        if obj.instance:
            return obj.instance.MODULE_TYPE
        return None

    def serialize_instance(self, obj: CourseModule):
        if not obj.instance:
            return None
        serializer_cls = cls_schema_mapper.get(obj.instance)
        if not serializer_cls:
            return None
        schema: Schema = serializer_cls()

        return schema.dump(obj.instance).data


""" Эта схема будет использована позже, но в другой вьюшке,
    так как в этой нам нужен только id и name"""
# # TODO: В некоторых кейсах тут ещё курс
# class CourseStatementSchema(Schema):
#     """
#         Serializer for Statements
#     """
#     id = fields.Integer(dump_only=True)
#     name = fields.String()
#     olympiad = fields.Boolean()
#     settings = fields.String()  # JsonType
#     time_start = fields.Integer()
#     time_stop = fields.Integer()
#     virtual_olympiad = fields.Boolean()
#     virtual_duration = fields.Integer()
#     course_module_id = fields.Method(serialize='serialize_course')
#     course = fields.Nested(CourseSchema)
#     problems = fields.Method(serialize='serialize_problems')
#     require_password = fields.Method(serialize='serialize_require_password')
#
#     def serialize_module_id(self, obj: Statement):
#         return getattr(obj.course_module, 'id', None)
#
#     # TODO: переписать это на фильтрацию в БД и переместить во views
#     def serialize_problems(self, obj: Statement) -> dict:
#         return {
#             rank: {
#                 'id': statement_problem.problem.id,
#                 'name': statement_problem.problem.name,
#             }
#             for rank, statement_problem in obj.StatementProblems.items()
#             if statement_problem.problem and not statement_problem.hidden
#         }
#
#     def serialize_require_password(self, obj: Statement) -> bool:
#         if obj.course:
#             return obj.course.require_password()
#         else:
#             return False




