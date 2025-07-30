from thsdk import THS
import pandas as pd
import time

with THS() as ths:
    response = ths.depth("USZA300033")
    print("单只五档:")
    if not response.is_success():
        print(f"错误信息: {response.err_info}")

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)

    response = ths.depth(["USZD123234", "USZD123184", "USZD123093", "USZD123093", ])
    print("多支五档:")
    if not response.is_success():
        print(f"错误信息: {response.err_info}")
    print(pd.DataFrame(response.get_result()))
    time.sleep(1)
