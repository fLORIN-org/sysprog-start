import mmap
import os
import time

MB = 1024 * 1024
STAGE = 20
print("pid", os.getpid(), flush=True)
print("1. start", flush=True)
time.sleep(STAGE)
data = mmap.mmap(-1, 300 * MB)
print("2. got 300 MB", flush=True)
time.sleep(STAGE)
for i in range(0, len(data), mmap.PAGESIZE):
    data[i] = 1
print("3. wrote to every page", flush=True)
time.sleep(STAGE)
data.close()
print("4. freed", flush=True)
time.sleep(STAGE)
