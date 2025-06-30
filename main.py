import time
import sys

print("--- SMOKE TEST: Stage 1 - Application script is starting. ---")
sys.stdout.flush() # 强制立刻输出，防止被缓冲

# 我们让程序在这里永远地循环下去，防止容器立刻退出
# 每 10 秒打印一次心跳信息
count = 0
while True:
    print(f"--- SMOKE TEST: Stage 2 - Heartbeat {count}... Application is alive. ---")
    sys.stdout.flush() # 强制立刻输出
    count += 1
    time.sleep(10)
