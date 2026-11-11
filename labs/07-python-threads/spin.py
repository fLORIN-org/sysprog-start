import os, threading, time


def spin():
    end = time.time() + 15
    while time.time() < end:
        pass


print("pid", os.getpid())
threads = [threading.Thread(target=spin) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
