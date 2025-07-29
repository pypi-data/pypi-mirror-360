import ctypes
import time

def prevent_sleep():
    print("禁止电脑进入休眠状态....")
    while True:
        time.sleep(1)
        # 防止计算机休眠
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
        with open('执行结果/env.txt', 'r', encoding='utf-8') as f:
            txt = f.read()
            if '执行完成:1' in txt:
                break

    print("允许电脑进入休眠状态....")