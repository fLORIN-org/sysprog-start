import sys, threading, time

N = 200_000_000


def work(n):
    while n:
        n -= 1


def run(k):
    threads = [threading.Thread(target=work, args=(N // k,)) for _ in range(k)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start


gil = sys._is_gil_enabled()
print(f"Python {sys.version.split()[0]}, GIL {'on' if gil else 'off'}")
for k in (1, 2, 4):
    print(f"{k} threads: {run(k):.2f} s")
