import datetime

from rmatics import db, create_app
from rmatics.model import CacheMeta


# Cron every hour
# 0 * * * * echo "прошёл один час"
def main():
    app = create_app()
    with app.app_context():
        db.session.query(CacheMeta). \
            filter(CacheMeta.when_expire < datetime.datetime.utcnow()) \
            .delete()

        db.session.commit()


if __name__ == '__main__':
    main()
