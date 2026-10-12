"""
Configuration module: env parsing, backend list, tunables.
"""

import os 

def load_config():
    port_str = os.getenv("LB_PORT","8080")
    backend_str = os.getenv("BACKENDS","")
    
    lb_port =  int(port_str)
    
    backends = [item.strip() for item in backend_str.split(",") if item.strip()]
    
    return lb_port,backends
