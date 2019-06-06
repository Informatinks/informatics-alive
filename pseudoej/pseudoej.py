import asyncio
import json
import os
import random

import requests
from aiohttp import web
from sqlalchemy import (
    Column, Integer, MetaData, Table, create_engine, asc)
from sqlalchemy_aio import ASYNCIO_STRATEGY

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://root:@localhost:3306/')
LISTENER_SERVICE_URI = os.getenv('LISTENER_SERVICE_URI', 'http://localhost:7777/')

engine = create_engine(SQLALCHEMY_DATABASE_URI, strategy=ASYNCIO_STRATEGY, echo=True)

metadata = MetaData()
ejudge_runs = Table(
    'runs', metadata,
    Column('run_id', Integer, primary_key=True),
    Column('contest_id', Integer),
    Column('prob_id', Integer),
    Column('status', Integer),
    schema='ejudge'
)

runs = Table(
    'runs', metadata,
    Column('id', Integer, primary_key=True),
    Column('ej_run_id', Integer),
    Column('ej_contest_id', Integer),
    schema='pynformatics'
)


async def get_run_id(contest_id: int) -> int:
    print('async task')

    conn = await engine.connect()
    query = ejudge_runs.select(ejudge_runs.c.contest_id == contest_id) \
        .where(ejudge_runs.c.status == 0) \
        .limit(1) \
        .offset(random.randint(1000, 10000))
    print(query)
    res = await conn.execute(query)
    res = await res.first()
    print(res)
    res = list(res)

    return res[0], res[1]


async def send_status_to_listener(run_id, contest_id, status_id):
    print('her')
    loop = asyncio.get_event_loop()
    args = {'run_id': run_id, 'contest_id': contest_id, 'status': status_id}
    args = '&'.join(f'{k}={v}' for k, v in args.items())
    future1 = loop.run_in_executor(None, requests.get, f'{LISTENER_SERVICE_URI}?{args}')

    resp = await future1
    print(resp)
    print(resp.text)


async def remove_run_from_rmatics(run_id, contest_id):
    conn = await engine.connect()

    res = await conn.execute(
        runs.select(runs.c.ej_contest_id == contest_id)
            .where(runs.c.ej_run_id == run_id)
            .order_by(asc('id')))
    run = await res.first()
    if not run:
        return
    id = run[0]
    await conn.execute(runs.delete(runs.c.id == id))


async def emulate_ejudge(run_id: int, contest_id: int):
    non_terminal = [96, 98]
    terminal = [0, 99, 8, 14, 9, 1, 10, 7, 11, 2, 3, 4, 5, 6]
    await remove_run_from_rmatics(run_id, contest_id)
    await send_status_to_listener(run_id, contest_id, random.choice(non_terminal))
    await send_status_to_listener(run_id, contest_id, random.choice(terminal))


async def handle(request):
    data = await request.post()  # json.loads(await request.text())
    if 'SID' in data:
        contest_id = data['SID']
        run_id, contest_id = await get_run_id(contest_id)
        request.loop.create_task(emulate_ejudge(run_id, contest_id))
        return web.Response(text=json.dumps({'run_id': run_id}))
    else:
        contest_id = data['contest_id']
        text = f'SID="{contest_id}";'
        return web.Response(text=text)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.post('/', handle)])

    web.run_app(app, port=11111)
