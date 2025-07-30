
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from latency_watch import LatencyWatch
from latency_watch.trace_config import TraceConfig

def level4():
    time.sleep(0.01)

def level3():
    time.sleep(0.01)
    level4()

def level2():
    time.sleep(0.01)
    level3()

def level1():
    time.sleep(0.01)
    level2()

@LatencyWatch.watch
def test_max_depth():
    TraceConfig.set(
        include_names=[],
        exclude_names=[],
        max_depth=2,  
        min_duration_ms=0,
        root_only=False
    )
    level1()

if __name__ == "__main__":
    LatencyWatch.reset()    
    test_max_depth()
    report = LatencyWatch.get_last_report()
    print("\n=== Max Depth Test (depth=2) ===")
    print("Should only show calls up to 2 levels deep")
    print(report if report else "No report generated")
