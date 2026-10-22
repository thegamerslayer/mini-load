"""
Main entry point: CLI arguments and uvicorn server startup.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path so running directly (python src/main.py) works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn
from src.config import get_config
from src.pool import Backend, Pool
from src.app import app
import logging




if __name__ == "__main__":
    lb_port, backend_urls = get_config()
    backend_objects = [Backend(f"backend-{i+1}", url) for i, url in enumerate(backend_urls)]
    
    pool = Pool(backend_objects)
    app.state.pool = pool

    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    
    print(f"Starting Door Helper on http://0.0.0.0:{lb_port}")
    print(
        f"Registered {len(backend_objects)} backends: {[b.url for b in backend_objects]}"
        )
    uvicorn.run(app, host="0.0.0.0", port=lb_port)