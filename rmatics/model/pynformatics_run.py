from flask import g

from rmatics.model import db
from rmatics.utils.functions import attrs_to_dict


class PynformaticsRun(db.Model):
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['run_id', 'contest_id'],
            ['ejudge.runs.run_id', 'ejudge.runs.contest_id'],
        ),
        {'schema': 'pynformatics'},
    )
    __tablename__ = 'run'

    run_id = db.Column('run_id', db.ForeignKey('ejudge.runs.run_id'), primary_key=True)
    contest_id = db.Column('contest_id', db.ForeignKey('ejudge.runs.contest_id'), primary_key=True)

    statement_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_statements.id'))
    source = db.Column(db.Text)

    run = db.relationship(
        'EjudgeRun',
        foreign_keys='[PynformaticsRun.run_id, PynformaticsRun.contest_id]',
        backref=db.backref('pynformatics_run', lazy='joined', uselist=False),
        lazy='joined'
    )
    statement = db.relationship('Statement', backref='pynformatics_runs')

    AUTHOR_ATTRS = [
        'source',
    ]

    def serialize(self, attributes=None):
        if not attributes:
            attributes = ('statement_id',)

        serialized = attrs_to_dict(self, *attributes)
        user = getattr(g, 'user', None)
        if user and self.run.user.id == user.id:
            serialized.update(attrs_to_dict(self, *PynformaticsRun.AUTHOR_ATTRS))
        return serialized
