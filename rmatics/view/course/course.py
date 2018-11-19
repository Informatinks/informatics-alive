from flask import (
    Blueprint,
    jsonify,
)
from flask.views import MethodView
from sqlalchemy import true
from werkzeug.exceptions import NotFound

from rmatics.model import db
from rmatics.model.course import Course
from rmatics.model.course_section import CourseSection
from rmatics.view.course.serializers.course import CourseSchema

course_blueprint = Blueprint('course', __name__, url_prefix='/course')


class CourseApi(MethodView):
    def get(self, course_id: int):

        course = db.session.query(Course).get(course_id)

        if not course:
            raise NotFound('Course with this id is not found')

        if not course.require_password():
            course.sections.filter(CourseSection.visible == true()).all()
            schema = CourseSchema()
        else:
            schema = CourseSchema(exclude=('sections',))

        dumped = schema.dump(course)

        return jsonify({'result': 'success', 'data': dumped.data})


course_blueprint.add_url_rule('/<int:course_id>', methods=('GET', ),
                              view_func=CourseApi.as_view('course'))
