import os
import shutil
from typing import Optional


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

        new_tests_location = os.path.join(problems_dir, 'tests')

        shutil.move(old_test_entry_dir_files_path, new_tests_location)

    return True


def try_to_move_checkers(contest_dir) -> bool:
    checkers_dir = os.path.join(contest_dir, 'checkers')
    if not os.path.isdir(checkers_dir):
        return False
    problems_dir = os.path.join(contest_dir, 'problems')

    for checker_name in os.listdir(checkers_dir):
        if checker_name.startswith('.'):
            continue
        problem_name = parse_problem_name(checker_name)
        if not problem_name:
            print(f'Пропускаем чекер {checker_name}')
            continue

        src = os.path.join(checkers_dir, checker_name)

        dest = os.path.join(problems_dir, problem_name, 'check')

        shutil.move(src, dest)


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
            contest_dir = os.path.join(os.getcwd(), dir)
            try_to_move_tests(contest_dir)
            try_to_move_checkers(contest_dir)
            with open(conf_path, 'a', encoding='utf-8') as conf:
                conf.write('\nadvanced_layout\n')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
