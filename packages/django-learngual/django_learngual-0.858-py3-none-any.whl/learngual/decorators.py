import cProfile
import functools
import io
import logging
import pstats
import time
from logging.handlers import RotatingFileHandler

from django.conf import settings


def profile_and_timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine project root (assume this file is always in project/subfolder/...)

        logs_dir = settings.ROOT_DIR / ".logs"
        logs_dir.mkdir(exist_ok=True)

        # Create .gitignore if not exists and ensure .logs is ignored
        gitignore_path = logs_dir / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w") as f:
                f.write(".logs/\n")
        else:
            with open(gitignore_path, "r+") as f:
                lines = f.readlines()
                if ".logs/\n" not in lines and ".logs/" not in [
                    line.strip() for line in lines
                ]:
                    f.write(".logs/\n")

        # Setup logger for this function
        log_file = logs_dir / f"{func.__qualname__}.log"
        logger = logging.getLogger(f"profile_and_timeit.{func.__qualname__}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=3)
            formatter = logging.Formatter("%(asctime)s %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        pr = cProfile.Profile()
        pr.enable()
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
        ps.print_stats()
        profile_report = s.getvalue()
        time_report = (
            f"[TIMEIT] {func.__qualname__} executed in {end - start:.6f} seconds"
        )

        logger.info(
            "\n[PROFILE REPORT for %s]\n%s%s\n",
            func.__qualname__,
            profile_report,
            time_report,
        )
        return result

    return wrapper


# Example usage:
# @profile_and_timeit
# def my_function():
#     ...

# class MyClass:
#     @profile_and_timeit
#     def my_method(self):
#         ...
