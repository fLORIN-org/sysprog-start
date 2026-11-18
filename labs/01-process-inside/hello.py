import ctypes

k32 = ctypes.windll.kernel32
k32.GetCurrentProcessId.restype = ctypes.c_ulong
print("agent v0 (python), pid=", k32.GetCurrentProcessId())
input("Press Enter to exit")
