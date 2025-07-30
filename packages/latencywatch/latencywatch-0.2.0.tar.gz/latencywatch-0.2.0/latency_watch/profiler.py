import functools
import inspect
from locale import currency
import re
import time
import threading
import sys

from latency_watch.trace_config import TraceConfig

_local = threading.local()

def get_call_stack():
    """Get the current thread's call stack."""
    if not hasattr(_local, 'call_stack'):
        _local.call_stack = []
    return _local.call_stack

def get_current_frame():
    """Get the current frame for tracking."""
    if not hasattr(_local, 'current_frame'):
        _local.current_frame = None
    return _local.current_frame

def set_current_frame(frame):
    """Set the current frame for tracking."""
    _local.current_frame = frame

class LatencyFrame:
    """Represents a single function call in the call hierarchy."""
    def __init__(self, func_name, depth=0):
        self.name = func_name
        self.start_time = time.time()
        self.end_time = None
        self.duration = None
        self.children = []
        self.parent = None
        self.depth = depth

    def finish(self):
        """Mark the frame as finished and calculate duration."""
        if self.end_time is None:
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time

    def get_self_time(self):
        """Calculate time spent in this function excluding children."""
        if self.duration is None:
            return 0.0
        child_time = sum(child.duration or 0.0 for child in self.children)
        return max(self.duration - child_time, 0.0)

    def to_dict(self, threshold_ms=0):
        if self.duration is None:
            self.finish()

        # Skip if below threshold
        if self.duration * 1000 < max(threshold_ms, TraceConfig.min_duration_ms):
            return None

        children_dicts = [
            child.to_dict(threshold_ms)
            for child in sorted(self.children, key=lambda x: x.start_time)
        ]
        children_dicts = [c for c in children_dicts if c is not None]

        return {
            "Name": self.name,
            "durationMs": round(self.duration * 1000, 2),
            "selfTimeMs": round(self.get_self_time() * 1000, 2),
            "children": children_dicts
        }

    def format(self, indent=0, threshold_ms=0):
        if self.duration is None:
            self.finish()

        if self.duration * 1000 < max(threshold_ms, TraceConfig.min_duration_ms):
            return ''

        duration_ms = self.duration * 1000
        self_time_ms = self.get_self_time() * 1000

        result = ' ' * indent + f"{self.name}: {duration_ms:.2f}ms (self: {self_time_ms:.2f}ms)\n"
        sorted_children = sorted(self.children, key=lambda x: x.start_time)
        for child in sorted_children:
            child_str = child.format(indent + 2, threshold_ms)
            if child_str:
                result += child_str
        return result


class TracingProfiler:
    """Profiler that uses sys.setprofile to track all function calls."""
    _active = False

    @classmethod
    def start(cls):
        if cls._active:
            return
        get_call_stack().clear()
        set_current_frame(None)
        cls._active = True
        sys.setprofile(cls._profile_handler)

    @classmethod
    def stop(cls):
        if not cls._active:
            return

        call_stack = get_call_stack()
        for frame in call_stack:
            if frame.duration is None:
                frame.finish()

        current = get_current_frame()
        while current:
            if current.duration is None:
                current.finish()
            current = current.parent

        sys.setprofile(None)
        cls._active = False

    @classmethod
    def _should_track(cls, frame):
        if not frame:
            return False

        code = frame.f_code
        func_name = code.co_name
        
        if func_name.startswith(('test_', 'level', 'root_', 'process_', 'handle_')):
            return True
            
        filename = code.co_filename
        if not filename or 'site-packages' in filename or filename.startswith(sys.base_prefix):
            return False
            
        # Skip special methods
        if func_name.startswith('__') and func_name.endswith('__'):
            return False
            
        # Skip modules we know we don't want to track
        module = inspect.getmodule(frame)
        if module:
            mod_name = module.__name__
            # Skip standard library and common modules
            if mod_name.startswith(('logging', 'threading', 'time', 'inspect', 'functools', 'os', 'sys')):
                return False
                
        return True
    
    @classmethod
    def _profile_handler(cls, frame, event, arg):
        # Skip our own module to avoid infinite recursion
        module_name = frame.f_globals.get('__name__', '')
        if module_name == __name__:
            return

        # Get function name and module info
        code = frame.f_code
        func_name = code.co_name
        filename = code.co_filename
        
        # Debug output
        debug = True
        if debug and event == 'call':
            print(f"[PROFILER] {event} {func_name} in {module_name} from {filename}")
        
        # Skip special methods and constructors
        if func_name in ('<module>', '<lambda>') or func_name.startswith('__'):
            if debug:
                print(f"[PROFILER] Skipping {func_name} (special method)")
            return
            
        # Get class name if this is a method
        if 'self' in frame.f_locals:
            instance = frame.f_locals['self']
            class_name = instance.__class__.__name__
            func_name = f"{class_name}.{func_name}"
        elif 'cls' in frame.f_locals and frame.f_locals['cls'] is not None:
            cls_obj = frame.f_locals['cls']
            if inspect.isclass(cls_obj):
                class_name = cls_obj.__name__
                func_name = f"{class_name}.{func_name}"

        call_stack = get_call_stack()
        current = get_current_frame()
        depth = current.depth + 1 if current else 0
        
        # Debug output
        debug = False
        if debug:
            print(f"[{event}] {func_name} (depth={depth})")

        # In root_only mode, we track the root function and all its direct children
        if TraceConfig.root_only:
            if event == 'call':
                if depth == 0:  # This is the root function
                    print(f"Root function: {func_name}")
                    latency_frame = LatencyFrame(func_name, depth=depth)
                    call_stack.append(latency_frame)
                    set_current_frame(latency_frame)
                elif depth == 1 and current and current.depth == 0:  # Direct child of root
                    print(f"Direct child: {func_name}")
                    if not TraceConfig.matches(func_name, depth):
                        return
                    latency_frame = LatencyFrame(func_name, depth=depth)
                    latency_frame.parent = current
                    current.children.append(latency_frame)
                    set_current_frame(latency_frame)
                else:  # Skip deeper calls
                    return
                return
                
            elif event == 'return':
                if current and (current.name == func_name or current.name.endswith(f".{func_name}")):
                    current.finish()
                    parent = current.parent
                    set_current_frame(parent)
                    # If returning from root, clear the current frame
                    if depth == 0:
                        set_current_frame(None)
                return
        
        if event == 'call':
            if not TraceConfig.matches(func_name, depth):
                return
                
            latency_frame = LatencyFrame(func_name, depth=depth)
            if current:
                latency_frame.parent = current
                current.children.append(latency_frame)
            else:
                call_stack.append(latency_frame)
            set_current_frame(latency_frame)
            
            if debug:
                print(f"  -> Tracking {func_name} at depth {depth}")

        elif event == 'return':
            if current and (current.name == func_name or current.name.endswith(f".{func_name}")):
                current.finish()
                set_current_frame(current.parent)
                if debug:
                    print(f"  <- Finished {func_name} in {current.duration*1000:.2f}ms")
            
        elif event == 'c_return' or event == 'c_exception':
            pass

class LatencyWatch:
    """
    Simple latency watching decorator that starts tracing for the decorated function.
    """
    @classmethod
    def watch(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Clear any previous state
            get_call_stack().clear()
            set_current_frame(None)
            
            # Start profiling
            if TraceConfig.root_only:
                sys.setprofile(TracingProfiler._profile_handler)
            else:
                TracingProfiler.start()
            
            try:
                # Call the wrapped function
                return func(*args, **kwargs)
            finally:
                # Stop profiling and clean up
                if TraceConfig.root_only:
                    sys.setprofile(None)
                else:
                    TracingProfiler.stop()
                
                # Ensure all frames are properly finished
                current = get_current_frame()
                while current:
                    if current.duration is None:
                        current.finish()
                    current = current.parent
                    
        return wrapper
    @classmethod
    def get_last_report(cls, as_dict=False, threshold_ms=0):
        call_stack = get_call_stack()
        if not call_stack:
            return "No calls recorded yet." if not as_dict else {}
        root = call_stack[0]  # Get the root frame
        return root.to_dict(threshold_ms) if as_dict else root.format(threshold_ms=threshold_ms)

    @classmethod
    def reset(cls):
        get_call_stack().clear()
        set_current_frame(None)