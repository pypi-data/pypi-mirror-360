
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from latency_watch import LatencyWatch
from latency_watch.trace_config import TraceConfig


TraceConfig.set(
    include_names=["important_"],  
    exclude_names=["skip_"],       
    max_depth=10,
    min_duration_ms=0,
    root_only=False
)

def skip_this():
    time.sleep(0.01)

def important_operation():
    time.sleep(0.02)
    skip_this() 

def regular_function():
    time.sleep(0.01)
    important_operation()

@LatencyWatch.watch
def test_include_exclude():
    important_operation()
    regular_function()
    skip_this()

if __name__ == "__main__":
    LatencyWatch.reset()
    test_include_exclude()
    report = LatencyWatch.get_last_report()
    print("\n=== Include/Exclude Test ===")
    print("Should only show test_include_exclude and important_operation")
    print(report if report else "No report generated")
