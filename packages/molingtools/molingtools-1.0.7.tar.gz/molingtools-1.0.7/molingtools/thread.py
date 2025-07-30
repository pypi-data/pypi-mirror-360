import asyncio
import ctypes
import inspect
import threading
import traceback

# 多线程
def threads_run(func, argslist: list, ifone=False, ifwait=True):
    ns = []
    for args in argslist:
        if ifone: args = (args,)
        n = threading.Thread(target=func, args=tuple(args))
        n.setDaemon(True)  # 设置为守护线程
        ns.append(n)
    [n.start() for n in ns]
    if ifwait: [n.join() for n in ns]


def thread_auto_run(arg_func, args, threadnum: int, ifwait=True, if_return_key_values=False, iftz=True,
                    max_error_num: int = 10, if_error=True) -> list or None:
    in_lock, out_lock = threading.Lock(), threading.Lock()
    args = list(args)
    length = len(args)
    results = list()
    error_num = 0

    def temp():
        nonlocal error_num
        # 接收返回值
        while True:
            with in_lock:
                if len(args) > 0:
                    arg = args.pop(0)
                else:
                    break
            try:
                result = arg_func(arg)
                with out_lock:
                    if if_return_key_values:
                        results.append([arg, result])
                    else:
                        results.append(result)
                    if iftz: print(f'\r{len(results)}/{length}', end='')
            except:
                traceback.print_exc()
                with in_lock:
                    error_num += 1
                    args.append(arg)
                    if iftz: print(f'\r{length - len(args)}/{length}', end='')
                    if error_num > max_error_num:
                        break

    ts = [threading.Thread(target=temp) for i in range(threadnum)]
    [t.start() for t in ts]
    if ifwait:
        [t.join() for t in ts]
        # 返回值判断错误情况
        if len(results) < length:
            error = f'{len(results)}/{length} 返回值小于输入值,因任务错误情况提前退出!'
            if if_error:
                raise ValueError(error)
            else:
                print(error)
        else:
            return results
    else:
        # 不等待不判断错误情况
        return None


# 协程运行
def tasksRun(*tasks):
    # 返回为list,序列对应协程序列
    if len(tasks) == 1:
        return asyncio.get_event_loop().run_until_complete(asyncio.gather(tasks[0]))
    else:
        return asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))


# 多任务分配
def getTasks(num, taskdatas):
    tasklen = len(taskdatas)
    if tasklen == 0: return []
    num = min(num, tasklen)
    cellnum = tasklen // num if tasklen % num == 0 else tasklen // num + 1
    tasks = list()
    for i in range(0, tasklen, cellnum):
        tasks.append(taskdatas[i:i + cellnum])
    return tasks


# 自定义线程类模型
class Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__alive = False

    def start(self):
        threading.Thread.start(self)
        self.__alive = True

    def stop(self):
        self.__alive = False
        stopThread(self)

    def is_alive(self):
        return threading.Thread.is_alive(self) and self.__alive


# 关闭线程
def stopThread(thread):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(thread.ident)
    if not inspect.isclass(SystemExit):
        exctype = type(SystemExit)
    else:
        exctype = SystemExit
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
