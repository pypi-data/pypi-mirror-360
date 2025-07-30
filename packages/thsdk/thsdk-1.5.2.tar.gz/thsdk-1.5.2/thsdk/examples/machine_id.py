from thsdk import THS
import time

with THS() as ths:
    print(f"machine ID: {ths.machine_id()}")
    time.sleep(1)
