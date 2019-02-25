import os
import sys
import time

import requests

SUBMISSIONS = ['data.cpp', 'data.py']

PROBLEM_ID = 2936
USER_ID = 1


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s function took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap


@timing
def send_submit(fd, problem_id, lang_id, user_id):
    _data = {
        'lang_id': lang_id,
        'user_id': user_id,
    }
    url = 'http://localhost:12346/problem/trusted/{}/submit_v2'.format(problem_id)
    _resp = requests.post(url, files={'file': fd}, data=_data)


@timing
def get_runs_table(problem_id):
    _ = requests.get('http://localhost:12346/problem/{}/submissions/'.format(problem_id))


def single_case(fd, lang_id, params: list):
    if 'send_submit' in params:
        send_submit(fd, PROBLEM_ID, lang_id, USER_ID)
    if 'get_table' in params:
        get_runs_table(PROBLEM_ID)


@timing
def main(params: list, times=1):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    files = [
        open(os.path.join(current_dir, SUBMISSIONS[0]), 'r'),
        open(os.path.join(current_dir, SUBMISSIONS[1]), 'r')
    ]

    langs = [3, 27]

    for _ in range(times):
        for lang, fd in zip(langs, files):
            single_case(fd, lang, params)
            fd.seek(0)
            time.sleep(0.2)


if __name__ == '__main__':
    arg = sys.argv[1]
    if arg == 'both':
        params = ['send_submit', 'get_table']
    else:
        params = [arg]
    main(params, 1)
