import ctypes
import faulthandler


def save(address):
    ctypes.memset(address, 0, 8)


faulthandler.enable()
print("writing 8 bytes to address 0", flush=True)
save(0)
print("not reached")
