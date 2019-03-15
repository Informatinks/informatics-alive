from rmatics import monitor_cacher
from rmatics.model import Run
from rmatics.view.monitors.monitor import get_runs


def invalidate_monitor_cache_by_run(run: Run):
    problem_id = run.problem_id
    user_id = run.user_id
    monitor_cacher.invalidate_all_of(get_runs, problem_id=problem_id, user_ids=user_id)