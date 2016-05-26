#!/usr/bin/env python3
import time

def ts():
    ts = str((int(time.time() * 100000)))
    return(ts)

if __name__ == "__main__":
    print(ts())
