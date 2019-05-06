import pymongo


def __should_stop(self):
    with self._lock:
        if self._stopped:
            self._thread_will_exit = True
            return True
        return False


def patched_PeriodicExecutor_run(self):
    """ This function will replace pymongo.periodic_executor.PeriodicExecutor.
        We have to do that because we have many deadlocks on original function.
        Unfortunately we lose some functionality like dynamic topology updating.
        Original source:
    def _run(self):
        while not self.__should_stop():
            try:
                if not self._target():
                    self._stopped = True
                    break
            except:
                with self._lock:
                    self._stopped = True
                    self._thread_will_exit = True

                raise

            deadline = _time() + self._interval

            while not self._stopped and _time() < deadline:
                time.sleep(self._min_interval)
                if self._event:
                    break  # Early wake.

            self._event = False
    """
    def __should_stop(self):
        with self._lock:
            if self._stopped:
                self._thread_will_exit = True
                return True
            return False

    while not __should_stop(self):
        try:
            self._target()
            self._stopped = True
            break
        except:
            with self._lock:
                self._stopped = True
                self._thread_will_exit = True
            raise


def patch_pymongo_to_avoiding_deadlocks():
    pymongo.periodic_executor.PeriodicExecutor._run = patched_PeriodicExecutor_run
