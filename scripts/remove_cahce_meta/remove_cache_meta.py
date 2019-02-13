import datetime

from rmatics import db, create_app
from rmatics.model import CacheMeta


# Cron every hour
# 0 * * * * echo "прошёл один час"
def main():
    current_time = datetime.datetime.utcnow()
    print(f'Job running at {current_time}')
    app = create_app()
    with app.app_context():
        db.session.query(CacheMeta). \
            filter(CacheMeta.when_expire < current_time) \
            .delete()

        db.session.commit()
    print('Success')


if __name__ == '__main__':
    main()
