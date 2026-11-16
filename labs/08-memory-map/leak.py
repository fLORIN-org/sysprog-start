import os
import time

print("pid", os.getpid(), flush=True)
kept = []
for second in range(60):
    kept.append(bytearray(10 * 1024 * 1024))
    time.sleep(1)
