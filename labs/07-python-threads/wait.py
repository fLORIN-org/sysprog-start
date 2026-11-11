import threading, time


def wait():
    time.sleep(2)


for k in (1, 4):
    threads = [threading.Thread(target=wait) for _ in range(k)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"{k} threads, each sleeps 2 s: {time.perf_counter() - start:.2f} s")
