import io

from bson import ObjectId
from flask import send_file, g, request
from flask.views import MethodView
from marshmallow import fields, Schema, post_load
from werkzeug.exceptions import NotFound, BadRequest

from rmatics.model.base import db, mongo
from rmatics.model.run import Run
from rmatics.view import require_auth, require_roles
from rmatics.utils.response import jsonify


class EjudgeRunSchema(Schema):
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


class SourceApi(MethodView):
    @require_auth
    def get(self, run_id: int):

        user_id = g.user.id

        run = db.session.query(Run).get(run_id)

        if run is None:
            raise NotFound()

        if run.user_id != user_id:
            # TODO: Rewrite permissions
            # This construction raises Forbidden if roles are not allowed
            require_roles('admin', 'teacher')(lambda *_, **__: None)()

        source = run.source

        # TODO: Придумать что-то получше для бинарных submission-ов
        return send_file(io.BytesIO(source), attachment_filename='submission.txt')


class ProtocolApi(MethodView):
    def get(self, run_id: int):

        run = db.session.query(Run).get(run_id)
        if not run:
            raise NotFound(f'run_id: {run_id} is not found')

        protocol = run.protocol
        if not protocol:
            raise NotFound(f'Protocol for run_id: {run_id} not found')

        return jsonify(protocol)


class UpdateEjudgeRun(MethodView):
    def post(self):
        data = request.get_json(force=True)
        ejudge_run_id = data['run_id']
        ejudge_contest_id = data['contest_id']
        mongo_protocol_id = data.get('mongo_protocol_id', None)

        run = db.session.query(Run) \
            .filter_by(ejudge_run_id=ejudge_run_id, ejudge_contest_id=ejudge_contest_id) \
            .one_or_none()

        if not run:
            msg = f'Cannot find Run with  \
                    ejudge_contest_id={ejudge_contest_id},  \
                    ejudge_run_id={ejudge_run_id}'
            raise BadRequest(msg)

        run_schema = EjudgeRunSchema(context={'instance': run})
        run, errors = run_schema.load(data)
        if errors:
            raise BadRequest(errors)

        if mongo_protocol_id:
            result = mongo.db.protocol.find_one_and_update({'_id': ObjectId(mongo_protocol_id)},
                                                           {'$set': {'run_id': run.id}})
            if not result['updatedExisting']:
                raise BadRequest(f'Cannot find protocol by _id {mongo_protocol_id}')

        db.session.add(run)
        db.session.commit()

        return jsonify({}, 200)
