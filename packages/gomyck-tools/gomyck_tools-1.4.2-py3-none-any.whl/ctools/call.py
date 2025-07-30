import sched
import threading
import time
from functools import wraps


# annotation
def once(func):
  """
  decorator to initialize a function once
  :param func: function to be initialized
  :return: the real decorator for return the result
  """
  initialized = False
  res = None

  def wrapper(*args, **kwargs):
    nonlocal initialized, res
    if not initialized:
      res = func(*args, **kwargs)
      initialized = True
      return res
    else:
      return res

  return wrapper


# annotation
def init(func):
  """
  decorator to initialize a function automic
  :param func: function to be initialized
  :return: the real decorator for return the result
  """
  res = func()

  def wrapper():
    return res

  return wrapper


# annotation
def schd(interval_seconds, start_by_call=False, run_now=False):
  scheduler = sched.scheduler(time.time, time.sleep)
  lock = threading.Lock()
  started = [False]  # 可变对象，线程可见
  print("schd delay is: ", interval_seconds)
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      def job():
        func(*args, **kwargs)
        scheduler.enter(interval_seconds, 1, job)
      def start_scheduler():
        with lock:
          if started[0]: return
          started[0] = True
          if run_now: func(*args, **kwargs)
          scheduler.enter(interval_seconds, 1, job)
          scheduler.run()
      threading.Thread(target=start_scheduler, daemon=True).start()
    # 如果不是手动触发，则自动启动一次（无参数）
    if not start_by_call: wrapper()
    return wrapper  # 如果是 start_by_call=True，返回 wrapper 让用户手动调用时带参
  return decorator
