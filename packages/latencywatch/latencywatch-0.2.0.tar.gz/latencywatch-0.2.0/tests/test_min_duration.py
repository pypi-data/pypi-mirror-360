
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from latency_watch import LatencyWatch
from latency_watch.trace_config import TraceConfig

def fast_function():
    pass 

def medium_function():
    time.sleep(0.005)  

def slow_function():
    time.sleep(0.015) 

@LatencyWatch.watch
def test_min_duration():
    TraceConfig.set(
        include_names=[],
        exclude_names=[],
        max_depth=10,
        min_duration_ms=10,  
        root_only=False
    )
    
    fast_function() 
    medium_function() 
    slow_function()   
    
    for _ in range(3):
        medium_function()  

if __name__ == "__main__":
    LatencyWatch.reset()    
    test_min_duration()
    report = LatencyWatch.get_last_report()
    print("\n=== Min Duration Test (10ms) ===")
    print("Should only show slow_function and the loop with medium_function")
    print(report if report else "No report generated")
