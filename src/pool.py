"""
Pool module: Backend class and the healthy/backend pool.
"""

from typing import List, Dict, Any, Optional

class Backend:
    def __init__(self,name: str,url:str, counters = None):
        self.name = name 
        self.url =  url
        self.counters = counters if counters is not None else {}
        
    def __repr__(self) -> str:
        return f"Backend(name='{self.name}', url='{self.url}')"
    
class Pool:
    def __init__(self,backends: Optional[List[Backend]] = None):
        self.backends: List[Backend] = backends if backends is not None else []
    
    def get_all_backends(self) -> List[Backend]:
        return self.backends
    