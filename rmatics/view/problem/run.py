import io

from flask import send_file, g, request
from flask.views import MethodView
from marshmallow import fields, Schema, post_load
from webargs.flaskparser import parser
from werkzeug.exceptions import NotFound, BadRequest

from rmatics.model.base import db, mongo
from rmatics.model.run import Run
from rmatics.utils.response import jsonify
from rmatics.view.problem.serializers.run import RunSchema


class FromEjudgeRunSchema(Schema):
    run_uuid = fields.String()
    score = fields.Integer()
    status = fields.Integer()
    lang_id = fields.Integer()
    test_num = fields.Integer()
    create_time = fields.DateTime()
    last_change_time = fields.DateTime()

    @post_load
    def load_ejudge_update(self, data: dict):
        run = self.context.get('instance')
        for k, v in data.items():
            setattr(run, f'ejudge_{k}', v)

        return run


class RunAPI(MethodView):
    def put(self, run_id: int):
        data = request.get_json(force=True, silent=False)

        run = db.session.query(Run).get(run_id)
        if run is None:
            raise NotFound(f'Run with id #{run_id} is not found')

        excludes = ['user', 'problem', 'create_time', 'ejudge_language_id']
        load_run_schema = RunSchema(exclude=excludes, context={'instance': run})
        run, errors = load_run_schema.load(data)

        if errors:
            raise BadRequest(errors)

        db.session.commit()

        dump_run_schema = RunSchema(exclude=excludes)
        data, errors = dump_run_schema.dump(run)

        return jsonify(data)


class SourceApi(MethodView):

    get_args = {
        'is_admin': fields.Boolean(default=False, missing=False),
        'user_id': fields.Integer(),
    }

    def get(self, run_id: int):
        args = parser.parse(self.get_args, request)
        is_admin = args.get('is_admin')
        user_id = args.get('user_id')

        run_q = db.session.query(Run)
        if not is_admin:
            run_q = run_q.filter(Run.user_id == user_id)

        run = run_q.filter(Run.id == run_id).one_or_none()

        if run is None:
            raise NotFound('Run with current id is not found')

        source = run.source or b''
        source = source.decode('utf_8')

        language_id = run.ejudge_language_id

        # TODO: Придумать что-то получше для бинарных submission-ов
        return jsonify({'source': source, 'language_id': language_id})


class ProtocolApi(MethodView):
    def get(self, run_id: int):

        run = db.session.query(Run).get(run_id)
        if run is None:
            raise NotFound('Current run_id is not found')

        protocol = run.protocol
        if protocol is None:
            raise NotFound('Protocol for current run_id not found')

        return send_file(io.BytesIO(protocol),
                         attachment_filename='submission.txt')


class UpdateFromEjudgeRun(MethodView):
    def post(self):
        data = request.get_json(force=True)
        ejudge_run_id = data['run_id']
        ejudge_contest_id = data['contest_id']
        protocol_uuid = data.get('mongo_protocol_uuid')

        run = db.session.query(Run)\
            .filter_by(ejudge_run_id=ejudge_run_id,
                       ejudge_contest_id=ejudge_contest_id)\
            .one_or_none()
        if not run:
            msg = f'Cannot find Run with ' \
                  f'ejudge_contest_id={ejudge_contest_id}, ' \
                  f'ejudge_run_id={ejudge_run_id}'
            raise BadRequest(msg)

        run_schema = FromEjudgeRunSchema(context={'instance': run})
        run, errors = run_schema.load(data)
        if errors:
            raise BadRequest(errors)

        if protocol_uuid:
            result = mongo.db.protocol.update({'protocol_id': protocol_uuid},
                                              {'protocol_id': run.id})
            if not result['updatedExisting']:
                raise BadRequest(f'Cannot find protocol by uuid {protocol_uuid}')

        db.session.add(run)
        db.session.commit()

        return jsonify({}, 200)
