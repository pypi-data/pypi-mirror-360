import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from latency_watch import LatencyWatch
from latency_watch.trace_config import TraceConfig

TraceConfig.set(
    include_names=[], 
    exclude_names=[],
    max_depth=10,
    min_duration_ms=0,
    root_only=True    
)

def deep_nested():
    time.sleep(0.01)

def nested_func():
    time.sleep(0.01)
    deep_nested()

def child_func():
    time.sleep(0.02)
    nested_func()

@LatencyWatch.watch
def root_function():
    child_func() 
    time.sleep(0.01) 
    child_func()  

if __name__ == "__main__":
    LatencyWatch.reset()
    root_function()    
    report = LatencyWatch.get_last_report()
    print("\n=== Root Only Test ===")
    print("Should only show root_function and its direct children (child_func and time.sleep)")
    print(report if report else "No report generated")
