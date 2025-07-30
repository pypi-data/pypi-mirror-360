

class TraceConfig:

    include_names = []
    exclude_names = []
    max_depth = None
    min_duration_ms = 0
    root_only = False


    @classmethod
    def set(cls,**kwargs):
        for k,v in kwargs.items():
            setattr(cls,k,v)

    
    @classmethod
    def matches(cls,func_name,depth):

        if any(ex in func_name for ex in cls.exclude_names):
            return False

        if cls.include_names:
            if not any(incl in func_name for incl in cls.include_names):
                return False

        if cls.max_depth is not None and depth > cls.max_depth:
            return False

        return True

