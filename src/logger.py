import logging
import os
import uuid
import json
import httpx
import asyncio
from logging import Handler, LogRecord
from typing import Optional

# The URL where the JS Worker listens for internal logs
# In a container, localhost:8080 is usually the worker if they share network, 
# but for Cloudflare Workers with Containers, we might need to use a specific URL.
# However, since the Worker *calls* the Container, the Container is the server.
# The Container needs to call *back* to the Worker. 
# If they are not on the same localhost, we need the Worker's public URL or a service binding.
# For now, we will assume we can hit the Worker via a configured environment variable WORKER_URL.
# If not set, we default to a placeholder that will fail gracefully.
WORKER_LOG_URL = os.getenv("WORKER_LOG_URL", "https://sgd-hbd-data.hacolby.workers.dev/_internal/log")

class HTTPHandler(Handler):
    """
    A custom logging handler that sends log records to the JS Worker via HTTP.
    """
    def __init__(self):
        super().__init__()
        self.client = httpx.AsyncClient(timeout=2.0)

    def emit(self, record: LogRecord):
        """
        Formats the log record and sends it to the Worker asynchronously.
        Note: Standard logging is synchronous. To avoid blocking, we should fire-and-forget 
        or use a background thread/queue. For simplicity in this environment, 
        we'll try to run it in the existing event loop if possible, or just use a sync call 
        if we want reliability over performance (though sync http is bad for logs).
        
        Better approach for production: QueueListener.
        For this MVP: We will use a sync call with a short timeout to ensure logs get out,
        OR just print to stdout (which Cloudflare captures) and rely on the Worker to parse it?
        
        Actually, the user specifically asked for "sent to a d1 table".
        Writing to D1 from Python requires an API call to the Worker.
        We will use `httpx.post` synchronously for now to ensure it happens, 
        but wrap it to catch errors so we don't crash the app.
        """
        try:
            log_entry = self.map_record_to_schema(record)
            
            # We need to send this payload to the worker.
            # Since emit is sync, we use a sync call or schedule a task.
            # If we are in an async loop (FastAPI), we can't easily "fire and forget" without a reference.
            # Let's use a simple sync post with short timeout.
            try:
                # Use a sync client for the emit method
                with httpx.Client(timeout=1.0) as client:
                    client.post(WORKER_LOG_URL, json=log_entry)
            except Exception as e:
                # Fallback to console if HTTP fails
                print(f"[LOG_FAIL] Could not send log to Worker: {e} | {json.dumps(log_entry)}")

        except Exception as e:
            print(f"Failed to process log record: {e}")

    def map_record_to_schema(self, record: LogRecord) -> dict:
        """
        Maps a LogRecord object to the schema expected by the Worker's log endpoint.
        """
        trace_id = getattr(record, 'traceId', None)
        
        # If no traceId in record, try to find it in context vars if we were using them
        # For now, default to None
        
        return {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
            "traceId": trace_id,
            "error": record.exc_text,
            "metadata": json.dumps(getattr(record, 'metadata', {}))
        }

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with both console and HTTP (D1) output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False 

    # Create handlers if they don't exist
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(traceId)s] - %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if not any(isinstance(h, HTTPHandler) for h in logger.handlers):
        http_handler = HTTPHandler()
        http_handler.setLevel(logging.INFO)
        logger.addHandler(http_handler)

    return logger

def get_logger_with_trace_id(name: str, trace_id: Optional[str] = None) -> logging.LoggerAdapter:
    """
    Returns a logger adapter that injects a traceId into all log records.
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    
    logger = setup_logger(name)
    adapter = logging.LoggerAdapter(logger, {'traceId': trace_id})
    return adapter

if __name__ == '__main__':
    print("--- Logger Example ---")
    log = get_logger_with_trace_id('test_logger')
    log.info("Test message to D1")


