import time
import traceback
from collections import OrderedDict
from flask import (
    g,
    jsonify,
    Blueprint
)
from sqlalchemy import and_

from rmatics.model.base import db
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.statement import Statement
from werkzeug.exceptions import InternalServerError
from rmatics.utils.exceptions import (
    RunAuthorOnly,
    RunNotFound,
)
from rmatics.view import (
    require_auth,
    require_roles,
)

protocol = Blueprint('protocol', __name__, url_prefix='/protocol')


# log = logging.getLogger(__name__)


# # signal_description = {
# #     1 : "Hangup detected on controlling terminal or death of controlling process",
# #     2 : "Interrupt from keyboard",
# #     3 : "Quit from keyboard",
# #     4 : "Illegal Instruction",
# #     6 : "Abort signal",
# #     7 : "Bus error (bad memory access)",
# #     8 : "Floating point exception",
# #     9 : "Kill signal",
# #     11 : "Invalid memory reference",
# #     13 : "Broken pipe: write to pipe with no readers",
# #     14 : "Timer signal",
# #     15 : "Termination signal"
# # }


# TODO: Переместить в view/run (/run/id/protocol), убрать вложеные try/except
@protocol.route('/get/<int:contest_id>/<int:run_id>')
def get_protocol(contest_id, run_id):
    try:
        run = EjudgeRun.get_by(run_id=run_id, contest_id=contest_id)
        try:
            run.fetch_tested_protocol_data()
            if run.user.statement \
                    .filter(Statement.olympiad == 1) \
                    .filter(Statement.time_stop > time.time()) \
                    .filter(Statement.time_start < time.time()) \
                    .count() == 0:
                res = OrderedDict()
                if run.tests:
                    sample_tests = run.problem.sample_tests.split(',')
                    for num in range(1, len(run.tests.keys()) + 1):
                        str_num = str(num)
                        if str_num in sample_tests:
                            res[str_num] = run.get_test_full_protocol(str_num)
                        else:
                            res[str_num] = run.tests[str_num]
                return jsonify({
                    'tests': res,
                    'host': run.host,
                    'compiler_output': run.compiler_output,
                })
            else:
                try:
                    return jsonify({
                        'tests': run.tests['1'],
                        'host': run.host,
                        'compiler_output': run.compiler_output,
                    })
                except KeyError as e:
                    return jsonify({'result' : 'error', 'message' : e.__str__(), "stack" : traceback.format_exc()})
        except Exception as e:
            return jsonify({'result' : 'error', 'message' : run.compilation_protocol, 'error' : e.__str__(), 'stack' : traceback.format_exc(), 'protocol': run.protocol})
    except Exception as e:
        return jsonify({'result': 'error', 'message' : e.__str__(), 'stack': traceback.format_exc(), 'protocol': run.protocol})


@protocol.route('/get_v2/<int:contest_id>/<int:run_id>')
@require_auth
def protocol_get_v2(contest_id, run_id):
    # TODO: переделать формат протокола (статус выдавать по id), избавиться от fetch_tested_protocol_data
    run = db.session.query(EjudgeRun) \
        .filter(
            and_(
                EjudgeRun.run_id == run_id,
                EjudgeRun.contest_id == contest_id
            )
        ) \
        .first()
    if not run:
        raise RunNotFound

    if g.user.ejudge_id != run.user_id:
        raise RunAuthorOnly

    try:
        run.fetch_tested_protocol_data()
    except Exception:
        raise InternalServerError

    tests_dict = OrderedDict()
    if run.tests:
        sample_tests = run.problem.sample_tests.split(',')
        for num in range(1, len(run.tests.keys()) + 1):
            str_num = str(num)
            if str_num in sample_tests:
                tests_dict[str_num] = run.get_test_full_protocol(str_num)
            else:
                tests_dict[str_num] = run.tests[str_num]

    return jsonify({
        'tests': tests_dict,
        'host': run.host,
        'compiler_output': run.compiler_output,
    })


@protocol.route('/get-full/<int:contest_id>/<int:run_id>')
@require_roles('admin', 'teacher', 'ejudge_teacher')
def protocol_get_full(contest_id, run_id):
    run = EjudgeRun.get_by(run_id=run_id, contest_id=contest_id)
    protocol = get_protocol(contest_id, run_id).json
    if protocol.get('result') == 'error':
        return protocol

    prot = protocol.get('tests', {})
    out_arch = None

    for test_num in prot:
        prot[test_num] = run.get_test_full_protocol(test_num)

    if out_arch:
        out_arch.close()

    full_protocol = {
        'tests': prot,
        'audit': run.get_audit(),
    }
    if protocol.get('compiler_output'):
        full_protocol['compiler_output'] = protocol['compiler_output']

    return jsonify(full_protocol)


# @view_config(route_name="protocol.get_test", renderer="string")
# @check_global_role(("teacher", "ejudge_teacher", "admin"))
# def protocol_get_test(request):
#     contest_id = int(request.matchdict['contest_id'])
#     run_id = int(request.matchdict['run_id'])
#     run = EjudgeRun.get_by(run_id = run_id, contest_id = contest_id)
#     prob = run.problem
#     return prob.get_test(int(request.matchdict['test_num']), prob.get_test_size(int(request.matchdict['test_num'])))


# @view_config(route_name="protocol.get_corr", renderer="string")
# @check_global_role(("teacher", "ejudge_teacher", "admin"))
# def protocol_get_corr(request):
#     contest_id = int(request.matchdict['contest_id'])
#     run_id = int(request.matchdict['run_id'])
#     run = EjudgeRun.get_by(run_id = run_id, contest_id = contest_id)
#     prob = run.problem
#     return prob.get_corr(int(request.matchdict['test_num']), prob.get_corr_size(int(request.matchdict['test_num'])))


# @view_config(route_name="protocol.get_outp", renderer="string")
# @check_global_role(("teacher", "ejudge_teacher", "admin"))
# def protocol_get_outp(request):
#     contest_id = int(request.matchdict['contest_id'])
#     run_id = int(request.matchdict['run_id'])
#     run = EjudgeRun.get_by(run_id = run_id, contest_id = contest_id)
#     return run.get_output_file(int(request.matchdict['test_num']), tp='o')


# @view_config(route_name="protocol.get_submit_archive", renderer="string")
# @check_global_role(("teacher", "ejudge_teacher", "admin"))
# def get_submit_archive(request):
#     contest_id = int(request.matchdict['contest_id'])
#     run_id = int(request.matchdict['run_id'])
#     sources = "sources" in request.params
#     all_tests = "all_tests" in request.params
#     tests = request.params.get("tests", "")
#     tests_set = set()
#     for i in tests.split(" "):
#         try:
#             tests_set.add(int(i))
#         except ValueError:
#             pass

#     run = EjudgeRun.get_by(run_id = run_id, contest_id = contest_id)
#     run.parsetests
#     prob = run.problem
#     archive = BytesIO()
#     zf = zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED)

#     run.fetch_tested_protocol_data()
#     for i in range(1, run.tests_count + 1):
#         if all_tests or i in tests_set:
#             zf.writestr("tests/{0:02}".format(i), prob.get_test(i, prob.get_test_size(i)))
#             zf.writestr("tests/{0:02}.a".format(i), prob.get_corr(i, prob.get_corr_size(i)))

#     if sources:
#         zf.writestr("{0}{1}".format(run_id, get_lang_ext_by_id(run.lang_id)), run.get_sources())

#     checker_src, checker_ext = prob.get_checker()
#     zf.writestr("checker{}".format(checker_ext), checker_src)

#     zf.close()
#     archive.seek(0)
#     response = Response(content_type="application/zip", content_disposition='attachment; filename="archive_{0}_{1}.zip"'.format(contest_id, run_id), body=archive.read())
#     return response
