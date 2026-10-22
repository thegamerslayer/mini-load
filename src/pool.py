"""
Pool module: Backend class and the healthy/backend pool.
"""
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class Backend:
    def __init__(self,name: str,url:str, counters = None, is_alive: bool = True):
        self.name = name 
        self.url =  url
        self.counters = counters if counters is not None else {}
        
        self.is_alive = is_alive
        self.consecutive_misses = 0
        self.consecutive_wins = 0
        
        
        self.unhealthy_transitions = 0
        self.healthy_transitions = 0

        # Clock times the tally board uses for its activity feed.
        self.status_changed_at = None
        self.last_unhealthy_at = None
        self.last_healthy_at = None
        
        
    def mark_success(self):
        self.consecutive_wins += 1
        self.consecutive_misses = 0

        # Only count/log an actual state transition
        if not self.is_alive and self.consecutive_wins >= 2:
            self.is_alive = True
            self.healthy_transitions += 1
            self.status_changed_at = time.time()
            self.last_healthy_at = self.status_changed_at

            logger.info(
                "[HEALTH] Backend %s rejoined rotation "
                "(healthy_transitions=%s)",
                self.name,
                self.healthy_transitions,
            )

    def mark_failure(self):
        self.consecutive_misses += 1
        self.consecutive_wins = 0

        # Only count/log an actual state transition
        if self.is_alive and self.consecutive_misses >= 3:
            self.is_alive = False
            self.unhealthy_transitions += 1
            self.status_changed_at = time.time()
            self.last_unhealthy_at = self.status_changed_at

            logger.warning(
                "[HEALTH] Backend %s ejected from rotation "
                "(unhealthy_transitions=%s)",
                self.name,
                self.unhealthy_transitions,
            )
            
    def __repr__(self) -> str:
        return (
            f"Backend("
            f"name='{self.name}', "
            f"url='{self.url}', "
            f"is_alive={self.is_alive}, "
            f"misses={self.consecutive_misses}, "
            f"wins={self.consecutive_wins}"
            f")"
        )
    
class Pool:
    def __init__(self,backends: Optional[List[Backend]] = None):
        self.backends: List[Backend] = backends if backends is not None else []
    
    def get_all_backends(self) -> List[Backend]:
        return self.backends
    