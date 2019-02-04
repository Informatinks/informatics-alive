from rmatics.utils.cacher import FlaskCacher

monitor_cacher = FlaskCacher(prefix='monitor', can_invalidate=True,
                             invalidate_by=['problem_id', 'user_ids'])
