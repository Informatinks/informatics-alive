from rmatics.model.base import db


class Role(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255))
    shortname = db.Column(db.Unicode(100))
    description = db.Column(db.UnicodeText)
    sortorder = db.Column(db.Integer)


class Context(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_context'

    id = db.Column(db.Integer, primary_key=True)
    contextlevel = db.Column(db.Integer)
    instanceid = db.Column(db.Integer)


class RoleAssignment(db.Model):
    __tablename__ = 'mdl_role_assignments'
    __table_args__ = {'schema': 'moodle'}

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column('roleid', db.Integer, db.ForeignKey('moodle.mdl_role.id'))
    context_id = db.Column('contextid', db.Integer, db.ForeignKey('moodle.mdl_context.id'))
    user_id = db.Column('userid', db.Integer, db.ForeignKey('moodle.mdl_user.id'))

    role = db.relationship('Role', lazy='joined')
    context = db.relationship('Context', lazy='joined')
