import time
import collections
import heapq
import select

from typing import Any, Coroutine, Union, Callable, Optional

SLEEP_TIME = .5


class QueueClosed(Exception):
    pass


class Awaitable:
    def __await__(self):
        yield


class Scheduler:

    def __init__(self):
        self._tasks_ready = collections.deque()
        self._tasks_delayed = []
        self._sequence = 0
        self._current = None
        self._read_waiting = {}
        self._write_waiting = {}

    def set_current(self, task: Optional['Task']) -> None:
        self._current = task

    def get_current(self) -> Optional['Task']:
        return self._current

    def add_to_tasks_ready(self, task: 'Task') -> None:
        self._tasks_ready.append(task)

    def call_soon(self, func: Callable[[...], Any], delayed: Union[int, float] = 0) -> None:
        ready = not bool(delayed)
        if delayed:
            self._sequence += 1
            deadline = time.time() + delayed
            heapq.heappush(
                self._tasks_delayed,
                (deadline, self._sequence, func)
            )
        if ready:
            self._tasks_ready.append(func)

    def read_wait(self, fileno, func):
        self._read_waiting[fileno] = func

    def write_wait(self, fileno, func):
        self._write_waiting[fileno] = func

    def run(self) -> None:

        while (
                self._tasks_ready
                or self._tasks_delayed
                or self._read_waiting
                or self._write_waiting
        ):

            if not self._tasks_ready:
                if self._tasks_delayed:
                    deadline, _, task = self._tasks_delayed[0]
                    timeout = deadline - time.time()
                    if timeout < 0:
                        timeout = 0
                if not self._tasks_delayed:
                    timeout = None
                can_read, can_write, _ = select.select(
                    self._read_waiting,
                    self._write_waiting,
                    [],
                    timeout
                )
                for file_descriptor in can_read:
                    self._tasks_ready.append(self._read_waiting.pop(file_descriptor))
                for file_descriptor in can_write:
                    self._tasks_ready.append(self._write_waiting.pop(file_descriptor))

                # Check for sleeping
                now = time.time()
                while self._tasks_delayed:
                    if now < self._tasks_delayed[0][0]:
                        break
                    self._tasks_ready.append(heapq.heappop(self._tasks_delayed)[2])


            while self._tasks_ready:
                task = self._tasks_ready.popleft()
                task()

    def add_task(self, coro: Coroutine[Any, Any, Any]) -> None:
        self._tasks_ready.append(Task(coro))

    @staticmethod
    def switch() -> Awaitable:
        return Awaitable()

    async def sleep(self, delay):
        self.call_soon(
            func=self._current,
            delayed=delay
        )
        self._current = None
        await self.switch()

    async def recv(self, sock, max_bytes):
        self.read_wait(sock, self._current)
        self._current = None
        await self.switch()
        return sock.recv(max_bytes)

    async def send(self, sock, data):
        self.write_wait(sock, self._current)
        self._current = None
        await self.switch()
        return sock.send(data)

    async def accept(self, sock):
        self.read_wait(sock, self._current)
        self._current = None
        await self.switch()
        return sock.accept()


scheduler = Scheduler()


class Task:

    def __init__(self, coro: Coroutine[Any, Any, Any]):
        self._coro = coro  # kind of wrapped coroutine

    # Make coroutine look like a callback. Imitating the asyncio.
    def __call__(self):
        try:
            # Driving a coroutine
            scheduler.set_current(self)
            self._coro.send(None)
            if scheduler.get_current():
                scheduler.add_to_tasks_ready(self)

        except (StopIteration,):
            pass


class AsyncQueue:

    def __init__(self, schler: Scheduler = scheduler):
        self._scheduler = schler
        self._items = collections.deque()
        self._waiting = collections.deque()
        self._closed = False

    def close(self) -> None:
        self._closed = True
        if self._waiting and not self._items:
            still_waiting_coro = self._waiting.popleft()
            self._scheduler.add_to_tasks_ready(still_waiting_coro)

    async def put(self, item):
        if self._closed:
            raise QueueClosed()

        self._items.append(item)
        if self._waiting:
            first_waiting_task = self._waiting.popleft()
            self._scheduler.add_to_tasks_ready(first_waiting_task)

    async def get(self):
        while not self._items:
            if self._closed:
                raise QueueClosed()
            self._waiting.append(self._scheduler.get_current())
            self._scheduler.set_current(None)
            await self._scheduler.switch()
        return self._items.popleft()


async def producer(q: AsyncQueue, amount: int) -> None:
    for i in range(amount):
        print(f'Produced {i}')
        await q.put(i)
        await scheduler.sleep(SLEEP_TIME)

    print(f'Producer done. Queue is getting closed.')
    q.close()


async def consumer(q: AsyncQueue) -> None:
    try:
        while True:
            item = await q.get()
            print(f'Consumed {item}')
    except QueueClosed:
        print(f'QueueClosed exception caught. Consumer done.')


# ... And these two functions are callback based. They should also work.

def count_down(start: int = 0) -> None:
    if start >= 0:
        print(f'Down {start}')
        scheduler.call_soon(
            lambda: count_down(start - 1),
            delayed=SLEEP_TIME * 2,
        )


def count_up(start: int = 0, stop: int = 0) -> None:
    def _do() -> None:
        nonlocal start
        if start <= stop:
            print(f'Up {start}')
            start += 1
            scheduler.call_soon(
                lambda: _do(),
                delayed=SLEEP_TIME
            )

    _do()


if __name__ == '__main__':
    from socket import socket, AF_INET, SOCK_STREAM

    q = AsyncQueue()


    scheduler.add_task(producer(q, 10))
    scheduler.add_task(consumer(q))

    scheduler.call_soon(lambda: count_down(start=10))
    scheduler.call_soon(lambda: count_up(stop=10))

    async def tcp_server(addr):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(addr)
        sock.listen(1)
        while True:
            client, _ = await scheduler.accept(sock)
            scheduler.add_task(echo_handler(client))


    async def echo_handler(client_socket):
        while True:
            data = await scheduler.recv(client_socket, 10000)
            if not data:
                break
            await scheduler.send(
                client_socket,
                b'Got: ' + data
            )
        print('Connection closed')
        client_socket.close()


    scheduler.add_task(
        tcp_server(('', 30001))
    )
    try:
        scheduler.run()
    except KeyboardInterrupt:
        pass
