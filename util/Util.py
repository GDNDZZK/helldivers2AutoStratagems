import threading


def run_in_thread(func):
    def wrapper(*args, **kwargs) -> threading.Thread:
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper