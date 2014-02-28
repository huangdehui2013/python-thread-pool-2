import threading 
import Queue

class PoolThread(threading.Thread):
    
    def __init__(self, requests_queue, wait_timeout, daemon, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.daemon = daemon
        self._queue = requests_queue
        self._wait_timeout = wait_timeout
        self._finished = threading.Event()
        self.start()

    def run(self):
        while True:
            if(self._finished.isSet()):
                break

            try:
                work = self._queue.get(block=True, timeout=self._wait_timeout)
            except Queue.Empty:
                continue
            else:
                try:
                    work.__call__()
                finally:
                    self._queue.task_done()

    

class ThreadPool:

    def __init__(self, pool_size, daemon=False, queue_size=0, wait_timeout=5):
        """Set up the thread pool and create pool_size threads
        """
        self._queue = Queue.Queue(queue_size)
        self._daemon = daemon
        self._threads = []
        self._pool_size = pool_size
        self._wait_timeout = wait_timeout
        self.createThreads()
        

    def addTask(self, callableObject):
        if (callable(callableObject)):
            self._queue.put(callableObject, block=True)

    def cleanUpThreads(self):
        self._queue.join()

        for t in self._threads:
            t._finished.set()

        
    def createThreads(self):
        for i in range(self._pool_size):
            self._threads.append(PoolThread(self._queue, self._wait_timeout, self._daemon))


class Fib:

    def __init__(self, num):
        self._num = num

    def fib(self, n):
        if n == 0: return 0
        if n == 1: return 1
        else: return self.fib(n-1) + self.fib(n-2)

    def __call__(self):
        print self._num, "=", self.fib(self._num)




if __name__ == '__main__':
    import multiprocessing

    cpu_count = multiprocessing.cpu_count()
    tp = ThreadPool(cpu_count * 2, queue_size=1, wait_timeout=1)
    for i in range(40):
        f = Fib(i)
        tp.addTask(f)

    tp.cleanUpThreads()
                                    
