from bson import ObjectId
from flask import request, current_app
from flask.views import MethodView
from marshmallow import fields, Schema, post_load
from webargs.flaskparser import parser
from werkzeug.exceptions import NotFound, BadRequest

from rmatics import monitor_cacher
from rmatics.model.base import db, mongo
from rmatics.model.run import Run
from rmatics.utils.response import jsonify
from rmatics.view.monitors.monitor import get_runs
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
        """ View for updating run """
        data = request.get_json(force=True, silent=False)

        run = db.session.query(Run).get(run_id)
        if run is None:
            raise NotFound(f'Run with id #{run_id} is not found')

        only_fields = ['ejudge_status', 'ejudge_test_num', 'ejudge_score']
        load_run_schema = RunSchema(only=only_fields, context={'instance': run})
        _, errors = load_run_schema.load(data)

        if errors:
            raise BadRequest(errors)

        # Avoid excess DB queries
        excludes = ['user', 'problem']
        dump_run_schema = RunSchema(exclude=excludes)
        data, _ = dump_run_schema.dump(run)

        db.session.add(run)
        db.session.commit()

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
        if not run:
            raise NotFound(f'run_id: {run_id} is not found')

        protocol = run.protocol
        if not protocol:
            raise NotFound(f'Protocol for run_id: {run_id} not found')

        return jsonify(protocol)


class UpdateRunFromEjudgeAPI(MethodView):

    def post(self):
        data = request.get_json(force=True)
        ejudge_run_id = data['run_id']
        ejudge_contest_id = data['contest_id']
        mongo_protocol_id = data.get('mongo_protocol_id', None)

        run = db.session.query(Run) \
            .filter_by(ejudge_run_id=ejudge_run_id,
                       ejudge_contest_id=ejudge_contest_id) \
            .one_or_none()

        if run is None:
            msg = f'Cannot find Run with  \
                    ejudge_contest_id={ejudge_contest_id},  \
                    ejudge_run_id={ejudge_run_id}'
            raise BadRequest(msg)

        run_schema = FromEjudgeRunSchema(context={'instance': run})
        received_run, errors = run_schema.load(data)
        if errors:
            raise BadRequest(errors)

        if mongo_protocol_id:
            # If it is we should invalidate cache
            self._invalidate_cache_by_run(run)
            current_app.logger.info('Cache invalidated')

            result = mongo.db.protocol.update_one({'_id': ObjectId(mongo_protocol_id)},
                                                  {'$set': {'run_id': received_run.id}})
            if not result.modified_count:
                raise BadRequest(f'Cannot find protocol by _id {mongo_protocol_id}')

        db.session.add(received_run)
        db.session.commit()

        return jsonify({}, 200)

    @classmethod
    def _invalidate_cache_by_run(cls, run):
        problem_id = run.problem_id
        user_id = run.user_id
        monitor_cacher.invalidate_all_of(get_runs, problem_id=problem_id, user_ids=user_id)
