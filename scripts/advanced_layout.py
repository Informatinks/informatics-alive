import os
import shutil
from typing import Optional
from rmatics.ejudge.serve_internal import EjudgeContestCfg


def is_int(i: str):
    try:
        int(i)
        return True
    except:
        return False


def check_is_advanced(fp):
    lines = fp.read()
    if 'advanced_layout' in lines:
        return True
    return False


def is_check_cmd(fp):
    fp.seek(0)
    text = fp.read()
    if 'check_cmd' in text:
        return True
    return False


def parse_problem_name(name: str) -> Optional[str]:
    if '.' in name:
        return None  # Так обрабатывается .dpr
    try:
        ch_names = name.split('_')
    except:
        raise ValueError(f'checker называется `{name}`, что делать...')
    if ch_names[0] != 'check':
        raise ValueError(f'checker называется `{name}`, что делать...')

    problem_name = '_'.join(ch_names[1:])
    return problem_name


# statements/A.xml
#            B.xml
# checkers/check_A
#          check_B
# tests/A/
#       B/
# problems/A/statement.xml
#            check
#            tests/
#          B/statement.xml
#            check
#            tests/
def try_to_move_tests(contest_dir) -> bool:
    dirs = os.listdir(contest_dir)
    if 'problems' in dirs:
        raise ValueError('Dir `problems` is already exists! What should ve do?')
    os.mkdir(os.path.join(contest_dir, 'problems'))
    problems_dir = os.path.join(contest_dir, 'problems')

    try:
        tests_entries_dir_names = os.listdir(os.path.join(contest_dir, 'tests'))
    except:
        raise ValueError('Dir `tests` does not exists. What should ve do?')
    for test_entry_dir_name in tests_entries_dir_names:
        if test_entry_dir_name.startswith('.'):
            continue

        old_test_entry_dir_files_path = os.path.join(contest_dir, 'tests', test_entry_dir_name)

        new_tests_location = os.path.join(problems_dir, test_entry_dir_name, 'tests')

        shutil.move(old_test_entry_dir_files_path, new_tests_location)

    return True


def try_to_move_checkers(contest_dir, checker_to_problem_mapper: dict) -> bool:
    checkers_dir = os.path.join(contest_dir, 'checkers')
    if not os.path.isdir(checkers_dir):
        return False
    problems_dir = os.path.join(contest_dir, 'problems')

    for checker_name in os.listdir(checkers_dir):
        if checker_name.startswith('.'):
            continue

        if checker_name in checker_to_problem_mapper:
            problem_name = checker_to_problem_mapper[checker_name]
        else:
            problem_name = parse_problem_name(checker_name)

        if not problem_name:
            print(f'Пропускаем чекер {checker_name}')
            continue

        src = os.path.join(checkers_dir, checker_name)

        dest = os.path.join(problems_dir, problem_name, 'check')

        shutil.move(src, dest)


def add_advanced_layout_option(conf_path: str):

    with open(conf_path, 'r') as fp:
        lines: list = fp.readlines()

    idx = 0
    for idx, line in enumerate(lines):
        if line.startswith('['):
            break

    if idx - 1 > 0:
        idx -= 1

    lines.insert(idx, 'advanced_layout')
    lines.insert(idx, '\n')
    lines.insert(idx, '\n')

    with open(conf_path, 'w') as fp:
        fp.writelines(lines)


def get_checker_problem_name_dict(config: EjudgeContestCfg):
    res = {}
    for _, problem in config.problems.items():
        if problem.check_cmd:
            res.update({problem.check_cmd: problem.short_name})
    return res


def main():
    dirs = os.listdir(os.getcwd())
    for dir in dirs:
        if not is_int(dir):
            continue
        print(dir)
        conf_path = os.path.join(os.getcwd(), dir, 'conf', 'serve.cfg')
        try:
            with open(conf_path, 'r', encoding='utf-8') as conf:
                is_advanced = check_is_advanced(conf)
                if is_advanced:
                    continue
                check_cmd = is_check_cmd(conf)

            contest_dir = os.path.join(os.getcwd(), dir)

            checker_problem_name_dict = {}
            if check_cmd:
                ejudge_config = EjudgeContestCfg(path=contest_dir + '/conf/serve.cfg')
                checker_problem_name_dict = get_checker_problem_name_dict(ejudge_config)

            try_to_move_tests(contest_dir)
            try_to_move_checkers(contest_dir, checker_problem_name_dict)

            add_advanced_layout_option(conf_path)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
