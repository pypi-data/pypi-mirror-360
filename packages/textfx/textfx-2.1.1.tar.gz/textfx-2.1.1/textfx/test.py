import time
import sys

width = 20
for _ in range(3):
    for i in list(range(width)) + list(range(width - 2, 0, -1)):
        sys.stdout.write('\r[' + ' ' * i + '●' + ' ' * (width - i - 1) + ']')
        sys.stdout.flush()
        time.sleep(0.05)

