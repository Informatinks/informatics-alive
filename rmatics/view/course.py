from flask import (
    Blueprint,
    g,
    jsonify,
)

from rmatics.view import load_course


course = Blueprint('course', __name__, url_prefix='/course')


@course.route('/<int:course_id>')
def course_get(course_id):
    load_course(course_id, silent=False)
    return jsonify(g.course.serialize())
