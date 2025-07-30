import os
import platform
import resource
import multiprocessing

class ResourceUtils:
    @staticmethod
    def extend_nofile_limit(new_limit: int = 100000) -> bool:
        """Attempts to increase the number of open file descriptors."""
        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            osname = platform.system()
            if osname in ["Linux", "Darwin"] and new_limit > soft:
                resource.setrlimit(resource.RLIMIT_NOFILE, (new_limit, hard))
            return True
        except Exception:
            return False

    @staticmethod
    def get_nofile_limit() -> tuple[int, int]:
        """Returns (soft, hard) NOFILE limits."""
        return resource.getrlimit(resource.RLIMIT_NOFILE)

    @staticmethod
    def get_max_memory() -> tuple[int, int]:
        """Returns (soft, hard) memory limits in bytes."""
        return resource.getrlimit(resource.RLIMIT_AS)

    @staticmethod
    def get_memory_usage_kb() -> int:
        """Returns current memory usage (approx) in KB."""
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return usage.ru_maxrss  # on Linux it's in KB, on macOS it's in bytes

    @staticmethod
    def get_cpu_time() -> float:
        """Returns total CPU time used (user + sys) in seconds."""
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return usage.ru_utime + usage.ru_stime

    @staticmethod
    def cpu_cores(logical: bool = True) -> int:
        """Returns number of CPU cores."""
        return multiprocessing.cpu_count() if logical else os.cpu_count()

    @staticmethod
    def get_stack_size() -> tuple[int, int]:
        """Returns (soft, hard) stack size limits in bytes."""
        return resource.getrlimit(resource.RLIMIT_STACK)

    @staticmethod
    def is_high_perf_env(min_fds: int = 65535) -> bool:
        """Check if the current system allows high open file handles."""
        soft, _ = ResourceUtils.get_nofile_limit()
        return soft >= min_fds
