# threaded_warnings.py

import warnings  as std_warnings
import threading



class WarningsProxy:
    
    def warn(self,message, category=None, stacklevel=1, source=None):
        thread_name = threading.current_thread().name
        if isinstance(message, str):
            message = f"[{thread_name}] {message}"
        if category is None:
            category = UserWarning
        std_warnings.warn(message, category=category, stacklevel=stacklevel + 1, source=source)
    

    def __getattr__(self, attr):
        # Proxy all other attributes to the real warnings module
        return getattr(std_warnings, attr)

# Export this as "warnings"
warnings = WarningsProxy()
