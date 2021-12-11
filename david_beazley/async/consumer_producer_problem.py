import queue
import threading
import time


def producer(q: queue.Queue, amount: int) -> None:
    for i in range(amount):
        print(f'Produced {i}')
        q.put(i)
        time.sleep(1)

    print(f'Producer done. Sentinel sent to queue.')
    q.put(None)


def consumer(q: queue.Queue) -> None:
    while True:
        item = q.get()
        if item is None:
            break
        print(f'Consumed {item}')
    print(f'Consumer done.')


if __name__ == '__main__':
    q = queue.Queue()
    threading.Thread(target=producer, args=(q, 10)).start()
    threading.Thread(target=consumer, args=(q,)).start()
