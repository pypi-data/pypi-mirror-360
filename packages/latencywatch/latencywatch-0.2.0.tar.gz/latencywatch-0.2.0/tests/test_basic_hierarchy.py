
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
    root_only=False
)

def level3():
    time.sleep(0.02)

def level2():
    time.sleep(0.01)
    level3()

def level1():
    time.sleep(0.01)
    level2()

def test_basic_hierarchy():
    level1()
    level1() 

if __name__ == "__main__":
    LatencyWatch.reset()    
    LatencyWatch.watch(test_basic_hierarchy)()    
    report = LatencyWatch.get_last_report()
    print("\n=== Test Basic Hierarchy ===")
    print(report if report else "No report generated")
