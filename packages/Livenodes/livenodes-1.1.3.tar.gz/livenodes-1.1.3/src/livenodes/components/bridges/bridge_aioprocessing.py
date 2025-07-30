import aioprocessing
from livenodes.components.computer import parse_location

from .bridge_abstract import Bridge

class Bridge_aioprocessing(Bridge):
    
    # _build thread
    # TODO: this is a serious design flaw: 
    # if __init__ is called in the _build / main thread, the queues etc are not only shared between the nodes using them, but also the _build thread
    # explicitly: if a local queue is created for two nodes inside of the same process computer (ie mp process) it is still shared between two processes (main and computer/worker)
    # however: we might be lucky as the main thread never uses it / keeps it.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # both threads
        self.queue = aioprocessing.AioJoinableQueue()
        self.closed_event = aioprocessing.AioEvent()
        
    # _computer thread
    def ready_send(self):
        pass

    # _computer thread
    def ready_recv(self):
        pass

    # _build thread
    @staticmethod
    def can_handle(_from, _to, _data_type=None):
        # can handle same process, and same thread, with cost 1 (shared mem would be faster, but otherwise this is quite good)
        from_host, from_process, from_thread = parse_location(_from)
        to_host, to_process, to_thread = parse_location(_to)
        # disable, as they don't actually seem to be better.
        # process & thread
        # ( python3 tests/dev.py; 1_000)  0.60s user 0.16s system 27% cpu 2.708 total
        # ( python3 tests/dev.py; 2_000)  0.68s user 0.21s system 31% cpu 2.806 total
        # # process & aio thread
        # ( python3 tests/dev.py; 1_000)  0.61s user 0.22s system 29% cpu 2.849 total
        # ( python3 tests/dev.py; 2_000)  0.77s user 0.30s system 35% cpu 2.977 total
        return False, 10
        # Only claim to be capable of thread bridges
        # return from_host == to_host and from_process == to_process, 2
    
        # ## IMPORTANT: the aio bridges are faster (threads) or as fast (processes) as the above implementations. However, i don't know why the feeder queues are not closed afterwards leading to multiple undesired consequences (including a broken down application)
        # THUS => only re-enable these if you are willing to debug and test that!

        # Technically we are also able of handling process bridges, but we are not going to claim that because of the warnign above
        # return from_host == to_host, 2


    # _from thread
    def close(self):
        self.info('Closing Bridge')
        if self.closed_event.is_set():
            return
        self.closed_event.set()
        self.queue.close()
        # self.queue = None
        # self.closed_event = None

    # _from thread
    def put(self, ctr, item):
        # # print('putting value', ctr)
        self.queue.put_nowait((ctr, item))

    # _to thread
    def closed(self):
        return self.closed_event.is_set()
    
    # _to thread
    def empty(self):
        return self.queue.empty() and self._read == {}
    
    def closed_and_empty(self):
        ret = self.closed() and self.empty()    
        self.debug(f'Checking if closed and empty: {ret}')
        return ret

    # _to thread
    async def onclose(self):
        await self.closed_event.coro_wait()
        await self.queue.coro_join()
        self.debug('Closed Event set and queue empty -- telling multiprocessing data storage')
        # this feels very hacky -yh
        self.close()

    # _to thread
    async def update(self):
        # # print('waiting for asyncio to receive a value')
        itm_ctr, item = await self.queue.coro_get()
        self._read[itm_ctr] = item
        self.queue.task_done()
        return itm_ctr
