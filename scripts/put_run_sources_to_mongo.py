from pymongo import MongoClient
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from rmatics.utils.run import safe_open, submit_path

engine = create_engine('mysql+pymysql://user:12345@localhost/informatics')

Base = declarative_base()

mongo = MongoClient('mongodb://localhost/test')


sources_path = 'archive/runs'


class Run(Base):
    __table_args__ = (
        {'schema': 'pynformatics'},
    )
    __tablename__ = 'runs'

    id = Column(Integer, primary_key=True)
    ejudge_run_id = Column('ej_run_id', Integer)
    ejudge_contest_id = Column('ej_contest_id', Integer)


def get_source(run: Run) -> str:
    path = submit_path(sources_path,
                                 run.ejudge_contest_id,
                                 run.ejudge_run_id)
    try:
        data = safe_open(path, 'rb').read()
    except FileNotFoundError:
        print(f'File not found: {path}')
        raise
    for encoding in ['utf-8', 'ascii', 'windows-1251']:
        try:
            data = data.decode(encoding)
        except:
            print('decoded:', encoding)
            pass
        else:
            break
    else:
        return 'Ошибка кодировки'
    return data


def put_to_mongo(run: Run, data: str):
    blob = data.encode('utf-8')
    mongo.db.source.insert_one({
        'run_id': run.id,
        'blob': blob,
    })


Session = sessionmaker(bind=engine)

session = Session()

if __name__ == '__main__':
    STARTS_WITH = 15882103
    PER_STEP_CNT = 1000
    quantity = session.query(Run).filter(Run.id >= STARTS_WITH).count()
    print(f'Total run quantity: {quantity}')
    steps_count = (quantity // PER_STEP_CNT) + 1
    for step in range(steps_count):
        print(f'Step from {step * PER_STEP_CNT} to {(step + 1) * PER_STEP_CNT}')
        runs_q = session.query(Run)\
                        .filter(Run.id >= STARTS_WITH)\
                        .order_by(Run.id)\
                        .limit(PER_STEP_CNT)\
                        .offset(step * PER_STEP_CNT)
        for run in runs_q:
            print(f'Process on run #{run.id} ({run.ejudge_contest_id}, {run.ejudge_run_id})')
            if run.ejudge_run_id is None or run.ejudge_contest_id is None:
                print('Run without ejudge run or contest')
                continue
            try:
                source = get_source(run)
            except FileNotFoundError as e:
                print(e.args)
                print(f'Can\'t find source for run #{run.id}')
                continue

            put_to_mongo(run, source)
            print('Success')
