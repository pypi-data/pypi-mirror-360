import threading
import functools


def run_async(func):
    @functools.wraps(func)
    def _run_async(*args, **kwargs):
        run_async_flag = kwargs.get('run_async', False)
        return_thread_flag = kwargs.get('return_thread', False)
        kwargs = kwargs.copy()
        kwargs.pop('run_async', None)
        kwargs.pop('return_thread', None)
        if run_async_flag:
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
            return thread if return_thread_flag else None
        else:
            return func(*args, **kwargs)
    return _run_async
