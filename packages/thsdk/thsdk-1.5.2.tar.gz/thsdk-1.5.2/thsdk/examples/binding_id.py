from thsdk import THS
import time

with THS() as ths:
    print(f"binding ID: {ths.binding_id()}")
    time.sleep(1)
