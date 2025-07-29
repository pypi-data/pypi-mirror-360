import functools
import time


def timer(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        elapsed = end - start
        print(f"Finished in {elapsed:.2f} seconds...")

        return result

    return inner


@timer
def _test_timer():
    time.sleep(0.121341)


if __name__ == "__main__":
    _test_timer()
