"""
Configuration module: env parsing, backend list, tunables.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_WEIGHTS = [3, 1, 1]

def get_config():
    port_str = os.getenv("LB_PORT","8080")
    backend_str = os.getenv("BACKENDS","")
    
    lb_port =  int(port_str)
    
    backends = [item.strip() for item in backend_str.split(",") if item.strip()]
    
    return lb_port,backends


def get_strategy_config():
    """Which choosing rule to start with, and its weights (Step 6)."""
    strategy = (os.getenv("LB_STRATEGY") or "round_robin").strip()
    weight_str = (os.getenv("LB_WEIGHTS") or "").strip()

    if weight_str:
        weights = [float(item) for item in weight_str.split(",") if item.strip()]
    else:
        weights = list(DEFAULT_WEIGHTS)

    return strategy, weights
