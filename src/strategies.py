"""
Strategies module: Round robin, weighted round robin, least connections, P2C.
"""
import itertools
from typing import Optional
from .pool import Backend, Pool

class RoundRobinBalancer:
    def __init__(self,pool: Pool):
        self.pool = pool
        backends = self.pool.get_all_backends()
        
        
        self._cycle = itertools.cycle(backends) if backends else None
        
    def round_robin(self) -> Optional[Backend]:
        backends = self.pool.get_all_backends()
        if not backends:
            return None
        
        if self._cycle is None:
            self._cycle = itertools.cycle(backends)
            
        backend = next(self._cycle)
        
        backend.counters["total_requests"] = backend.counters.get("total_requests",0) + 1
        
        return backend