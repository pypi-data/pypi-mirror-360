import threading
import time
from collections import defaultdict
from functools import wraps
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

ENABLE_PROFILING = os.getenv("ENABLE_PROFILING") == "1"

# 每个线程注册的上下文：{thread_id: ctx}
_thread_contexts = {}
_context_lock = threading.Lock()

def _get_context():
    thread_id = threading.get_ident()
    with _context_lock:
        if thread_id not in _thread_contexts:
            _thread_contexts[thread_id] = {
                'counters': defaultdict(lambda: {'count': 0, 'time': 0}),
                'call_stack': []
            }
        return _thread_contexts[thread_id]

# 全局聚合后的数据（最终用于输出）
_global_counters = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'time': 0}))


def profile(arg=None):
    # 如果装饰器写法是 @profile
    if callable(arg):
        func = arg
        func_name = func.__qualname__

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not ENABLE_PROFILING:
                return func(*args, **kwargs)

            ctx = _get_context()
            stack = ctx['call_stack']
            counters = ctx['counters']

            start_time = time.perf_counter_ns()
            stack.append((func_name, start_time, 0))

            result = func(*args, **kwargs)

            end_time = time.perf_counter_ns()
            total_time = end_time - start_time
            _, _, child_time = stack.pop()
            exclusive_time = total_time - child_time

            counters[func_name]['count'] += 1
            counters[func_name]['time'] += exclusive_time

            if stack:
                parent_name, parent_start, parent_child_time = stack[-1]
                stack[-1] = (parent_name, parent_start, parent_child_time + total_time)

            return result

        return wrapper

    else:
        # 装饰器调用时带参数了，比如 @profile("访问数据库")
        label = arg

        def decorator(func):
            func_name = label or func.__qualname__

            @wraps(func)
            def wrapper(*args, **kwargs):
                if not ENABLE_PROFILING:
                    return func(*args, **kwargs)

                ctx = _get_context()
                stack = ctx['call_stack']
                counters = ctx['counters']

                start_time = time.perf_counter_ns()
                stack.append((func_name, start_time, 0))

                result = func(*args, **kwargs)

                end_time = time.perf_counter_ns()
                total_time = end_time - start_time
                _, _, child_time = stack.pop()
                exclusive_time = total_time - child_time

                counters[func_name]['count'] += 1
                counters[func_name]['time'] += exclusive_time

                if stack:
                    parent_name, parent_start, parent_child_time = stack[-1]
                    stack[-1] = (parent_name, parent_start, parent_child_time + total_time)

                return result

            return wrapper

        return decorator



class ScopedTimer:
    def __init__(self, label):
        self.label = label
        self.enabled = ENABLE_PROFILING

    def __enter__(self):
        if self.enabled:
            self.ctx = _get_context()
            self.start = time.perf_counter_ns()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enabled:
            duration = time.perf_counter_ns() - self.start
            self.ctx['counters'][self.label]['count'] += 1
            self.ctx['counters'][self.label]['time'] += duration


def dump_stats():
    with _context_lock:
        for tid, ctx in _thread_contexts.items():
            counters = ctx['counters']
            for name, stats in counters.items():
                _global_counters[tid][name]['count'] += stats['count']
                _global_counters[tid][name]['time'] += stats['time']
            counters.clear()

    thread_count = len(_global_counters)
    merged_stats = defaultdict(lambda: {'count': 0, 'time': 0})
    for funcs in _global_counters.values():
        for name, stats in funcs.items():
            merged_stats[name]['count'] += stats['count']
            merged_stats[name]['time'] += stats['time']

    result = "concurrency,label_or_func,call_count,avg_self_time_us\n"
    for name, stats in sorted(merged_stats.items()):
        count = stats['count']
        total_time_ns = stats['time']
        avg_time_us = (total_time_ns / count) / 1000  if count > 0 else 0
        result += f"{thread_count},{name},{count},{avg_time_us:.0f}\n"

    return result


def reset_stats():
    with _context_lock:
        _global_counters.clear()
        for ctx in _thread_contexts.values():
            ctx['counters'].clear()


class ProfilerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get':
            stats = dump_stats()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain;charset=utf-8')
            self.end_headers()
            self.wfile.write(stats.encode('utf-8'))
        elif self.path == '/reset':
            reset_stats()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Stats reset successfully')
        else:
            self.send_response(404)
            self.end_headers()


def start_server():
    if not ENABLE_PROFILING:
        return 
    
    port = int(os.getenv('PROFILING_HTTP_PORT', '8089'))
    print(f"start to listen {port}\n")
    server = HTTPServer(('0.0.0.0', port), ProfilerHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server

# ================== 示例测试 ==================

# @profile
# def a():
#     time.sleep(0.2)
#     with ScopedTimer("step1-db-query"):
#         time.sleep(0.3)
#     with ScopedTimer("step2-calc"):
#         time.sleep(0.4)

# @profile
# def worker(tid):
#     time.sleep(0.1)
#     for _ in range(2):
#         a()

# @profile
# def run_threads():
#     threads = []
#     for i in range(4):
#         t = threading.Thread(target=worker, args=(i,))
#         threads.append(t)
#         t.start()
#     for t in threads:
#         t.join()

# if __name__ == "__main__":
#     print(f"Profiler enabled? {ENABLE_PROFILING}")
#     run_threads()
#     print(dump_stats())
#     start_server()
#     while True:
#         time.sleep(1)
#         run_threads()
